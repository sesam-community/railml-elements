FROM python:3-alpine
MAINTAINER Ashkan Vahidishams "ashkan.vahidishams@sesam.io"

COPY ./service /service

RUN apk update
RUN apk add python-dev libxml2-dev libxslt-dev py-lxml musl-dev gcc
RUN apk add git
RUN apk add openssh

RUN pip install --upgrade pip

RUN pip install -r /service/requirements.txt

EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["./service/xml-service.py"]

