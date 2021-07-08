import email
from email.header import decode_header
import html2text
import json
import os
import urllib.parse
from shared.file_util import file_util
from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)


def get_from(email_message):
    from_raw = email_message.get_all('From', [])
    from_list = email.utils.getaddresses(from_raw)
    logger.debug("from_list=%s", from_list)

    if len(from_list) > 0:
        if len(from_list[0]) == 1:
            return from_list[0][0]
        if len(from_list[0]) == 2:
            return from_list[0][1]

    return "UnknownEmail"


def get_subject(email_message):
    subject = email_message.get("Subject")
    if subject is None:
        return "No Subject"

    subject, encoding = decode_header(str(subject))[0]
    return str(subject).strip()


def parse_body(message):
    email_body = {}
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                email_body["Plain_HTML"] = html2text.html2text(part.get_payload())
                email_body["HTML"] = part.get_payload()

            if part.get_content_type() == 'text/plain':
                email_body["Plain_Text"] = part.get_payload()
    else:
        if message.get_content_type() == 'text/html':
            email_body["Plain_HTML"] = html2text.html2text(message.get_payload())
            email_body["HTML"] = message.get_payload()

        if message.get_content_type() == 'text/plain':
            email_body["Plain_Text"] = message.get_payload()
    return email_body

def save_attachments(message, dest_dir):
    email_attachments = []
    if message.is_multipart():
        for part in message.walk():
            file_path = save_attachment(part, dest_dir)
            if file_path is not None:
                email_attachments.append(file_path)
    return email_attachments

def save_attachment(part, dest_dir):
    logger.error("save_attachement with file %s", part.get_filename())
    if bool(part.get_filename()):
        file_path = os.path.join(dest_dir, part.get_filename())
        file_path = urllib.parse.unquote(file_path)
        logger.debug(f"saving cv to file {file_path}")
        with open(file_path, 'wb') as file:
            file.write(part.get_payload(decode=True))

        return str(file_path)

def to_json_file(metadata, filename, dest_dir):
    logger.debug(f"trying to write json to file={filename} with uid={metadata['uid']}")
    json_obj = json.dumps(metadata, indent=4)
    file_path = file_util.write_to_file(json_obj, filename, dest_dir)
    return file_path
