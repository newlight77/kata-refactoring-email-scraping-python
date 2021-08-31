import email
import html2text
from email.header import decode_header
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
            logger.info("save_attachement with file %s", part.get_filename())
            if bool(part.get_filename()):
                file_path = file_util.write_to_file(part.get_payload(decode=True), part.get_filename(), dest_dir)
                logger.debug(f"saved cv to file {file_path}")
                if file_path is not None:
                    email_attachments.append(file_path)

    return email_attachments
