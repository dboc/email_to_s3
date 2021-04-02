from os import getenv, path, mkdir
import json
import re
import time
import logging as log

from minio import Minio

import imaplib
from email import utils
from email import message_from_string
from email import header
from unidecode import unidecode

def check_required_env(env, env_name):
    if not env:
        raise Exception(f"ENV Variables {env_name} not found")

# region ENV Variables
IMAP_HOST = getenv('IMAP_HOST', '')
check_required_env(IMAP_HOST, 'IMAP_HOST')
IMAP_PORT = getenv('IMAP_PORT', '')
check_required_env(IMAP_PORT, 'IMAP_PORT')
# IMAP_TLS = getenv('IMAP_TLS', '')
IMAP_USER = getenv('IMAP_USER', '')
check_required_env(IMAP_USER, 'IMAP_USER')
IMAP_PASSWD = getenv('IMAP_PASSWD', '')
check_required_env(IMAP_PASSWD, 'IMAP_PASSWD')
IMAP_FOLDER_PROCESSED = getenv('IMAP_FOLDER_PROCESSED', '')
check_required_env(IMAP_FOLDER_PROCESSED, 'IMAP_FOLDER_PROCESSED')
IMAP_FOLDER_OTHERS = getenv('IMAP_FOLDER_OTHERS', '')
check_required_env(IMAP_FOLDER_OTHERS, 'IMAP_FOLDER_OTHERS')
# IMAP_FOLDER_QUEUE = getenv('IMAP_FOLDER_QUEUE', '')
IMAP_FOLDER_DELETED = getenv('IMAP_FOLDER_DELETED', '\\Deleted')
IMAP_FOLDER_FLAGS = getenv('IMAP_FOLDER_FLAGS', '+FLAGS')
FILTER_FROM = getenv('FILTER_FROM', '')
check_required_env(FILTER_FROM, 'FILTER_FROM')
FILTER_ATTACHS = getenv('FILTER_ATTACHS', '')
# FILTER_SUBJECT = getenv('FILTER_SUBJECT', '')
# FILTER_TO = getenv('FILTER_TO', '')
SCRIPT_FOLDER = getenv('SCRIPT_FOLDER', path.join(path.abspath(path.dirname(__file__)),"temp"))
MINIO_SERVER = getenv('MINIO_SERVER', '')
check_required_env(MINIO_SERVER, 'MINIO_SERVER')
MINIO_ACCESS_KEY = getenv('MINIO_ACCESS_KEY', '')
check_required_env(MINIO_ACCESS_KEY, 'MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = getenv('MINIO_SECRET_KEY', '')
check_required_env(MINIO_SECRET_KEY, 'MINIO_SECRET_KEY')
MINIO_BUCKET = getenv('MINIO_BUCKET', '')
check_required_env(MINIO_BUCKET, 'MINIO_BUCKET')
# endregion ENV Variables

log.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log.INFO)

# variables
version="1.1"
imap_host=IMAP_HOST
imap_port=int(IMAP_PORT)
imap_folder_processed=IMAP_FOLDER_PROCESSED
imap_folder_deleted=IMAP_FOLDER_DELETED
imap_folder_flags=IMAP_FOLDER_FLAGS
imap_folder_others=IMAP_FOLDER_OTHERS
user_name=IMAP_USER
passwd=IMAP_PASSWD
filter_from=FILTER_FROM
filter_attachs = ''

if FILTER_ATTACHS:
    filter_attachs = dict()    
    for tmp_key_value in FILTER_ATTACHS.strip().split(','):
        tmp_key_value = tmp_key_value.strip()
        key, value = tmp_key_value.split(':')
        filter_attachs[key] = value

# folder_path=path.abspath(path.dirname(__file__)).join("messages")
folder_path=SCRIPT_FOLDER
search_regex=""

minio_url=MINIO_SERVER
access_key=MINIO_ACCESS_KEY
secret_key=MINIO_SECRET_KEY
bucket_name=MINIO_BUCKET
metadata_file="msg-metadata.json"

list_message = list()

if not path.isdir(folder_path) and not folder_path == "":
        mkdir(folder_path)

# imap connection
log.info(f"Script Version: {version}")
log.info(f"Conecting to {imap_host}:{imap_port}")
imap_zimbra = imaplib.IMAP4(host=imap_host,port=imap_port)
res, msg_res = imap_zimbra.starttls()
log.info(f"{res}:{msg_res}")
# imap login
log.info(f"Login {user_name}")
res, msg_res = imap_zimbra.login(user_name, passwd)
log.info(f"{res}:{msg_res}")
# imap select Inbox
log.info(f"Enter 'Inbox'")
res, msg_res = imap_zimbra.select()
log.info(f"{res}:{msg_res}")
# look all msg
log.info(f"Search ALL 'Inbox'")
res, msg = imap_zimbra.search(None, 'ALL')    
log.info(f"{res}:{msg_res}")

for id_msg in msg[0].split():
    log.info(f"Fetch msg {id_msg}")
    res, data = imap_zimbra.fetch(id_msg, '(RFC822)')
    log.info(f"{res}:{msg_res}")
    
    res, uid = imap_zimbra.fetch(id_msg, 'UID')
        
    # create message dict
    message = dict()
    message['id'] = id_msg
    message['uid'] = uid[0].decode('utf-8').replace(" ","-")
    # message['from'] = ""
    # message['subject'] = ""
    # message['date'] = ""
    # message['folder'] = ""   
    # message['body_text'] = ""
    # message['body_html'] = "" 
    # message['attachs'] = list() 

    # # create imap_msg -> utf8 to convert byte literal to string removing type b'
    mime_data = data[0][1]
    raw_email_string = mime_data.decode('utf-8')
    imap_msg = message_from_string(raw_email_string)

    # set From addr
    message['from'] = unidecode(imap_msg.get('From'))
    
    # set subject
    tmp_sbj, tmp_charset = header.decode_header(
                            imap_msg.get('Subject'))[0]
    if(tmp_charset is None):
        message['subject'] = tmp_sbj
    else:
        message['subject'] = unidecode(tmp_sbj.decode(tmp_charset))
    
    # set date
    message['date'] = imap_msg.get('Date')
    
    log.info(f"From: {message['from']} Subject: {message['from']} Date: {message['date']}")
    
    if filter_from in message['from']:
        log.info(f"Message has from {filter_from} and will be saved")
        # set folder - folder name is epochdate
        epoch = time.mktime(utils.parsedate(message['date']))
        # folder_name = f"{int(epoch)}_{message\['from'\]}"
        folder_name = f"{int(epoch)}"
        message['folder'] = path.join(folder_path,folder_name)
        if not path.isdir(message['folder']):
            mkdir(message['folder'])

        message['body_text'] = ""
        message['body_html'] = "" 
        message['attachs'] = list() 

        if imap_msg.is_multipart():            
            # set attachs and body
            # downloading attachments and body                                      
            for part in imap_msg.walk():
                content_type = part.get_content_type()
                content_maintype =  part.get_content_maintype()
                content_disposition = part.get('Content-Disposition')
                                                                
                if content_type == 'text/plain':                
                    message['body_text'] = part.get_payload()
                    continue
                if content_type == 'text/html':                
                    message['body_html'] = part.get_payload()
                    continue            
                if content_maintype == 'multipart':
                    continue
                if content_disposition is None:
                    continue

                if bool(part.get_filename()):                    
                    tmp_fn, tmp_charset = header.decode_header(
                                            part.get_filename())[0]
                    if(tmp_charset is None):
                        file_name = unidecode(tmp_fn)
                    else:
                        file_name = unidecode(tmp_fn.decode(tmp_charset))               
                                        
                    message['attachs'].append(file_name)
                    attach_path = path.join(message['folder'], file_name)

                    log.info(f"Saving attach:  {file_name} in {attach_path}")
                    fp = open(attach_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()                                        
        else:            
            # extract content type of email
            content_type = imap_msg.get_content_type()
            # get the email body        
            if content_type == "text/plain":
                message['body_text'] = imap_msg.get_payload()            
            else:            
                message['body_html'] = imap_msg.get_payload()

        metadata_msg_path = path.join(message['folder'],metadata_file)    
        message['id'] = message['id'].decode('utf-8')
        metadata = json.dumps(message, indent=4, sort_keys=True)

        log.info(f"Saving metadata:  {metadata_file} in {metadata_msg_path}")
        fp = open(metadata_msg_path, 'w')
        fp.write(str(metadata))
        fp.close()                
        
        log.info(f"Moving to Folder {imap_folder_processed}")
        res, msg_res = imap_zimbra.copy(message['id'], imap_folder_processed)
        log.info(f"{res}:{msg_res}")
        if res == 'OK':
            res, msg_res = imap_zimbra.store(message['id'], imap_folder_flags, imap_folder_deleted)
            log.info(f"{res}:{msg_res}")
        list_message.append(message)
    else:
        log.info(f"Message has not from {filter_from}")        
        log.info(f"Moving to Folder {imap_folder_others}")
        res, msg_res = imap_zimbra.copy(message['id'], imap_folder_others)
        if res == 'OK':
            mov, data = imap_zimbra.store(message['id'], imap_folder_flags, imap_folder_deleted)
        
# imap_zimbra.expunge()         
# res, msg = imap_zimbra.search(None, 'ALL')    
log.info(f"Logout and closing connection")
res, msg = imap_zimbra.close()
log.info(f"{res}:{msg_res}")
res, msg = imap_zimbra.logout()
log.info(f"{res}:{msg_res}")   

# Create a client with the MinIO server
log.info(f"Conecting to Minio {minio_url}")   
client = Minio(
    minio_url,
    access_key=access_key,
    secret_key=secret_key,
    region='br'
)
# # Upload messages
for msg_minio in list_message:    
    prefix = path.relpath(msg_minio['folder'],folder_path)

    path_metadata = path.join(msg_minio['folder'], metadata_file)
    log.info(f"Copy to bucket:{bucket_name} File: {prefix}-{metadata_file} Path: {path_metadata}")
    client.fput_object(
        bucket_name, f"{prefix}-{metadata_file}", path_metadata,
    )

    for at_name in msg_minio['attachs']:
        path_attach = path.join(msg_minio['folder'], at_name)

        if filter_attachs:
            for pattern,rename in filter_attachs.items():                
                if(re.match(pattern,at_name,re.IGNORECASE)):                                        
                    log.info(f"Copy to bucket:{bucket_name} File: {rename}")
                    client.fput_object(
                        bucket_name, f"{rename}", path_attach,
                    )
        else:
            log.info(f"Copy to bucket:{bucket_name} File: {prefix}-{at_name}")
            client.fput_object(
                bucket_name, f"{prefix}-{at_name}", path_attach,
            )

log.info(f"Sucess!")
