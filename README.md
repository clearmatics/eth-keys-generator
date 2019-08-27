# ibft-keys-generator
Generate ethereum keys and write it to Kubernetes Secrets and ConfigMaps

## External Dependencies
- docker 18.09.2  
- kube-apiserver v1.11.8

Data will be added to existing secrets and ConfigMaps by %name%


| type      | name                  | keys                     |
|-----------|-----------------------|--------------------------|
| secret    | %name% | `private_key`          | 
| ConfigMap | %name% | `pub_key`, `address` | 


# Build
```
docker build -t eth-keys-generator .
```

# Usage

Run and connect to remote kubernetes cluster using default local kube config
```
./cm_writer/main.py -k remote -namespace test -name testaccount
```

Run and connect to kube-apiserver from internal pod (inside kubernetes cluster)
```
docker run -ti clearmatics/eth-keys-generator
```

# Options
```
usage: main.py [-h] [-k {pod,remote}] [-n NAMESPACE] [--validators VALIDATORS]
               [--observers OBSERVERS]

Generate set of keys for initialising the network and deploy it to kubernetes
etcd

optional arguments:
  -h, --help            show this help message and exit
  -k {pod,remote}       Type of connection to kube-apiserver: pod or remote
                        (default: pod)
  -n NAMESPACE          Kubernetes namespace.
  --validators VALIDATORS
                        number of validators. Should be more than 4 for ibft
```


# Get secret from ConfigMap

Get private key

```bash
NAMESPACE=test
NAME=testname
kubectl -n $NAMESPACE get secrets $NAME -o 'go-template={{index .data "private_key"}}' | base64 --decode; echo ""
```

Get address
```bash
NAMESPACE=test
NAME=testname
kubectl -n $NAMESPACE get configmap $NAME -o yaml |grep .address

```
