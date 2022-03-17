FROM python:3.9.10-buster
WORKDIR /usr/src/app
RUN pip install tabulate pause pandas
COPY k8s-pvc-dump.py .
CMD [ "python", "./k8s-pvc-dump.py" ]
