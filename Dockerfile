FROM python:3
RUN pip3 install unidecode minio
RUN git clone https://github.com/dboc/email_to_s3.git /app
WORKDIR /app
ENV TZ=America/Sao_Paulo
#CMD ["python","-u","./app.py"]