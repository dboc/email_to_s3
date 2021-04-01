### About me
 I am developer as hobby. For me automate boring stuff is a pleasure, no more operational work :)
 > "Live as if you were to die tomorrow. Learn as if you were to live forever" Mahatma Gandhi.

### Donate
 if you like the project and it help you, you could give me some reward for that.

|Donate via PayPal| Top Donation   | Lastest Donation   |
|---|---|---|
|[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=PCTDXQTW2H59G&source=url) |  -  |  -  |


# Email IMAP to S3 MinIO

> Python Script - Email(IMAP) to S3 MinIO

This is a specific script that read an Email via IMAP protocol and redirect the attachs and some message metadata to S3 MinIO

## How It Works

The script goes through all message in the folder 'INBOX', then select those email that are from specific address and send it to a S3 MinIO 


## Requirements 
 - python3
 - python library: unidecode, minio

## Installation
First you have to install library unidecode and minio

```
pip3 install unidecode minio

```

Then just execute script.py

```
git clone https://github.com/dboc/email_to_s3.git
export IMAP_HOST=
export IMAP_PORT=
export IMAP_USER=
export IMAP_PASSWD=
export IMAP_FOLDER_PROCESSED=
export IMAP_FOLDER_OTHERS=
export FILTER_FROM=
export MINIO_SERVER=
export MINIO_ACCESS_KEY=
export MINIO_SECRET_KEY=
export MINIO_BUCKET=
python3 script.py
```

or ...

You could make a container image and run it

```
git clone https://github.com/dboc/email_to_s3.git
docker build -t YOUR_REPORSITORY/YOUR_NAME_IMG .
docker push YOUR_REPORSITORY/YOUR_NAME_IMG
# docker run with enviroment variables seet config set
```

## Config

To fit your enviromment and needs, you must change the default envoriments in app.py or set then.

```python
...
IMAP_HOST = getenv('IMAP_HOST', '')
IMAP_PORT = getenv('IMAP_PORT', '')
# IMAP_TLS = getenv('IMAP_TLS', '')
IMAP_USER = getenv('IMAP_USER', '')
IMAP_PASSWD = getenv('IMAP_PASSWD', '')
IMAP_FOLDER_PROCESSED = getenv('IMAP_FOLDER_PROCESSED', '')
IMAP_FOLDER_OTHERS = getenv('IMAP_FOLDER_OTHERS', '')
# IMAP_FOLDER_QUEUE = getenv('IMAP_FOLDER_QUEUE', '')
IMAP_FOLDER_DELETED = getenv('IMAP_FOLDER_DELETED', '\\Deleted')
IMAP_FOLDER_FLAGS = getenv('IMAP_FOLDER_FLAGS', '+FLAGS')
FILTER_FROM = getenv('FILTER_FROM', '')
# FILTER_SUBJECT = getenv('FILTER_SUBJECT', '')
# FILTER_TO = getenv('FILTER_TO', '')
SCRIPT_FOLDER = getenv('SCRIPT_FOLDER', path.join(path.abspath(path.dirname(__file__)),"temp"))
MINIO_SERVER = getenv('MINIO_SERVER', '')
MINIO_ACCESS_KEY = getenv('MINIO_ACCESS_KEY', '')
MINIO_SECRET_KEY = getenv('MINIO_SECRET_KEY', '')
MINIO_BUCKET = getenv('MINIO_BUCKET', '')
...
```

## Usage example

Change enviroment variables in app.py.

```python
...
export IMAP_HOST=
export IMAP_PORT=
export IMAP_USER=
export IMAP_PASSWD=
export IMAP_FOLDER_PROCESSED=
export IMAP_FOLDER_OTHERS=
export FILTER_FROM=
export MINIO_SERVER=
export MINIO_ACCESS_KEY=
export MINIO_SECRET_KEY=
export MINIO_BUCKET=
...
```
Then execute:
```
python script.py
```

After that you would see the output:
```
2021-04-01 11:28:18,277 INFO:Conecting to ...
.
.
.
```

## Contributing

1. Fork it (<https://github.com/dboc/email_handler_attach.git>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request