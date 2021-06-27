import email
from email.header import decode_header
import html2text
from imapclient import IMAPClient
import json
import os
import urllib.parse
from config import config
from shared.collections_util import dict_util
from shared.file_util import file_util
from config import logger

logger = logger.logger(__name__, config.LOG_LEVEL)

def run():
    # pylint: disable=no-member
    scraper_config = dict_util.DefDictToObject({
        'host': config.EMAIL_HOST,
        'email': config.EMAIL,
        'password': config.EMAIL_PASSWORD,
        'folder': config.FOLDER,
        'attachment_dir': config.ATTACHMENTS_DIR,
        'timeout': 15,
        'read_post_action': config.EMAIL_READ_POST_ACTION,
        'search_key_words': config.EMAIL_SEARCH_KEYWORDS.split(',')
    })

    imap = connect(scraper_config)
    scraper = EmailScraper()

    listen(imap, scraper, scraper_config)


def connect(config):
    imap = IMAPClient(config.host)
    imap.login(config.email, config.password)
    return imap


def listen(imap, scraper, config):

    # if type(imap) is not IMAPClient:
    #    raise ValueError("imap must be of type IMAPClient")

    scraper.scrape(imap, config)

    imap.idle()
    logger.info("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            logger.info("imap sent: %s", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                scraper.scrape(imap, config)

                imap.idle()  # idling
    except ValueError as ve:
        logger.error(f"error: {ve}")
    except KeyboardInterrupt as ki:
        logger.error(f"error: {ki}")
    finally:
        logger.info("terminating the app")
        imap.idle_done()
        imap.logout()


class EmailScraper():

    def scrape(self, imap, config):
        # if type(imap) is not IMAPClient:
        #    raise ValueError("imap must be of type IMAPClient")

        metadatas = []

        imap.select_folder(config.folder, readonly=False)
        messages = imap.search([config.search_key_words])
        raw_envelopes = imap.fetch(messages, ['ENVELOPE']).items()
        raw_emails = imap.fetch(messages, 'RFC822').items()
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            envelop = raw_envelop[b'ENVELOPE']
            date = envelop.date.strftime('%Y%m%d_%H%M')

            message = email.message_from_bytes(raw_message[b'RFC822'])
            email_from = self.__get_from(message)
            subject = message.get("Subject")
            subject, encoding = decode_header(str(subject))[0]
            email_subject = str(subject).strip()
            logger.info(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")
            email_body = {}
            email_attachments = []
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == 'text/html':
                        email_body["Plain_HTML"] = html2text.html2text(part.get_payload())
                        email_body["HTML"] = part.get_payload()

                    if part.get_content_type() == 'text/plain':
                        email_body["Plain_Text"] = part.get_payload()

                    if bool(part.get_filename()):
                        file_path = os.path.join(config.attachment_dir, part.get_filename())
                        file_path = urllib.parse.unquote(file_path)
                        logger.info(f"saving cv to file {file_path}")
                        with open(file_path, 'wb') as file:
                            file.write(part.get_payload(decode=True))
                        email_attachments.append(file_path)
            else:
                if message.get_content_type() == 'text/html':
                    email_body["Plain_HTML"] = html2text.html2text(message.get_payload())
                    email_body["HTML"] = message.get_payload()

                if message.get_content_type() == 'text/plain':
                    email_body["Plain_Text"] = message.get_payload()

            metadatas.append({
                'uid': uid,
                'from': email_from,
                'subject': email_subject,
                'date': date,
                # 'body': email_body,
                'attachments': email_attachments
            })

        for metadata in metadatas:
            try:
                json_obj = json.dumps(metadata, indent=4)
                filename = f"{metadata['from']}-{metadata['date']}-{metadata['uid']}.json"
                file_path = file_util.write_to_file(json_obj, filename, config.attachment_dir)
            except ValueError:
                continue

    def __get_from(self, email_message):
        from_raw = email_message.get_all('From', [])
        from_list = email.utils.getaddresses(from_raw)

        if len(from_list[0]) == 1:
            return from_list[0][0]

        if len(from_list[0]) == 2:
            return from_list[0][1]

        return "UnknownEmail"
