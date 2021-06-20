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
    listen(imap, scraper_config)


def connect(config):
    imap = IMAPClient(config.host)
    imap.login(config.email, config.password)
    return imap


def listen(imap, config):

    if type(imap) is not IMAPClient:
        raise ValueError("imap must be of type IMAPClient")

    imap.idle()
    print("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            print("imap sent:", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                summary = scrape(imap, config)
                summary_to_json_file(summary, config.attachment_dir)

                imap.idle()  # idling
    except ValueError as ve:
        print(f"error: {ve}")
    except KeyboardInterrupt as ki:
        print(f"error: {ki}")
    finally:
        print("terminating the app")
        imap.idle_done()
        imap.logout()


def scrape(imap, config) -> dict:
    if type(imap) is not IMAPClient:
        raise ValueError("imap must be of type IMAPClient")

    emails_summary = {}

    imap.select_folder(config.folder, readonly=False)
    messages = imap.search([config.search_key_words])
    raw_envelopes = imap.fetch(messages, ['ENVELOPE']).items()
    raw_emails = imap.fetch(messages, 'RFC822').items()
    for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
        envelop = raw_envelop[b'ENVELOPE']
        date = envelop.date.strftime('%Y%m%d_%H%M')

        message = email.message_from_bytes(raw_message[b'RFC822'])
        email_from = get_from(message)
        email_subject = get_subject(message).strip()
        print(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")

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
                    file_path = save_attachment(part, config.attachment_dir)
                    email_attachments.append(file_path)
        else:
            if message.get_content_type() == 'text/html':
                email_body["Plain_HTML"] = html2text.html2text(message.get_payload())
                email_body["HTML"] = message.get_payload()

            if message.get_content_type() == 'text/plain':
                email_body["Plain_Text"] = message.get_payload()

        emails_summary[uid] = {
            'uid': uid,
            'from': email_from,
            'subject': email_subject,
            # 'body': email_body,
            'attachments': email_attachments
        }
    return emails_summary


def get_from(email_message) -> str:
    from_raw = email_message.get_all('From', [])
    from_list = email.utils.getaddresses(from_raw)

    if len(from_list[0]) == 1:
        return from_list[0][0]

    if len(from_list[0]) == 2:
        return from_list[0][1]

    return "UnknownEmail"


def get_subject(email_message) -> str:
    subject = email_message.get("Subject")
    if subject is None:
        return "No Subject"

    subject, encoding = decode_header(str(subject))[0]
    return str(subject).strip()


def save_attachment(part, dest_dir) -> str:
    if bool(part.get_filename()):
        file_path = os.path.join(dest_dir, part.get_filename())
        file_path = urllib.parse.unquote(file_path)
        print(f"save cv to file {file_path}")
        with open(file_path, 'wb') as file:
            file.write(part.get_payload(decode=True))

    return str(file_path)


def summary_to_json_file(summary, dest_dir) -> list:
    file_list = []
    print(f'summary={summary}')
    for key in summary.keys():
        try:
            json_obj = json.dumps(summary[key], indent=4)
            filename = f"{key}.json"
            file_path = file_util.write_to_file(json_obj, filename, dest_dir)
            file_list.append(file_path)
        except ValueError:
            continue

    return file_list
