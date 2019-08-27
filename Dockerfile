FROM python:3.7.3-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /env/cm_writer
ADD ./cm_writer/requirements.txt .
RUN pip install -r ./requirements.txt
RUN apk del .build-deps gcc musl-dev
COPY ./cm_writer /cm_writer

ENTRYPOINT ["/cm_writer/main.py"]
CMD []
