FROM python:3.6.9-buster
WORKDIR /usr/src/app
RUN pip install tabulate pause pandas
COPY k8s-pvc-dump/ .
CMD [ "python", "./k8s-pvc-dump.py" ]
