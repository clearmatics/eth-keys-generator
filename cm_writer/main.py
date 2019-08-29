#!/usr/bin/env python

import base64
import argparse
import sha3
from kubernetes import client, config
from ecdsa import SigningKey, SECP256k1


def checksum_encode(addr_str):
    keccak = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak.update(addr.encode('ascii'))
    hash_addr = keccak.hexdigest()
    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c
    return '0x' + out


def generate_keys():
    # Based on https://github.com/vkobel/ethereum-generate-wallet/blob/master/ethereum-wallet-generator.py
    keccak = sha3.keccak_256()

    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key().to_string()

    keccak.update(pub)
    address = keccak.hexdigest()[24:]
    return {'private_key': priv.to_string().hex(), 'pub_key': pub.hex(), 'address': checksum_encode(address)}


def write_keys(wallet, name, namespace):
    api_instance = client.CoreV1Api()

    sec = client.V1Secret()
    sec.type = 'Opaque'

    cmap = client.V1ConfigMap()

    sec.data = {'private_key': base64.b64encode(wallet['private_key'].encode()).decode()}
    cmap.data = {'address': wallet['address'], 'pub_key': wallet['pub_key']}

    api_instance.patch_namespaced_secret(name, namespace, sec)
    api_instance.patch_namespaced_config_map(name, namespace, cmap)


def main():
    parser = argparse.ArgumentParser(description='Generate set of keys for initialising the network and deploy it to kubernetes etcd')
    parser.add_argument('-k',
                        dest='kubeconf_type',
                        default='pod',
                        choices=['pod', 'remote'],
                        help='Type of connection to kube-apiserver: pod or remote (default: %(default)s)'
                        )
    parser.add_argument('--namespace',
                        dest='namespace',
                        default='default',
                        help='Kubernetes namespace.'
                        )
    parser.add_argument('--name',
                        dest='name',
                        help='Name that will used for Kubernetes ConfigMap and Secret)'
                        )
    args = parser.parse_args()

    if args.kubeconf_type == 'pod':
        config.load_incluster_config()
        f = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
        namespace = f.readline()
        f.close()
    elif args.kubeconf_type == 'remote':
        config.load_kube_config()
        namespace = args.namespace

    wallet = generate_keys()
    write_keys(wallet, args.name, namespace)


if __name__ == '__main__':
    main()
