import email
from email.header import decode_header
import html2text
from imapclient import IMAPClient
import json
import os
import urllib.parse
from shared.file_util import file_util
from domain.email_scraper_hexagonal import EmailScraperPort


class EmailClientHexagonal:
    def __init__(self, imap, config):
        self.imap = imap
        self.config = config

    def connect(self):
        self.imap = self.imap or IMAPClient(self.config.host)
        self.imap.login(self.config.email, self.config.password)
        return self

    def fetch_emails(self):
        print(f"fetch emails with imap={self.imap}")
        self.imap.select_folder(self.config.folder, readonly=False)
        messages = self.imap.search(self.config.search_key_words)
        raw_envelopes = self.imap.fetch(messages, ['ENVELOPE']).items()
        raw_emails = self.imap.fetch(messages, 'RFC822').items()

        raw_emails_with_envelopes = []
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            print(f"fetch emails: yield UID={uid}")
            message = email.message_from_bytes(raw_message[b'RFC822'])
            envelop = raw_envelop[b'ENVELOPE']
            raw_emails_with_envelopes.append((uid, message, envelop))
        return raw_emails_with_envelopes


class EmailScraperAdapter(EmailScraperPort):
    # pylint: disable=too-many-arguments
    def __init__(self, emailClient: EmailClientHexagonal, config):
        self.client = emailClient
        self.config = config

    def connect(self):
        return self.client.connect()

    def scrape(self):
        return self.client.fetch_emails()


def get_from(email_message):
    from_raw = email_message.get_all('From', [])
    from_list = email.utils.getaddresses(from_raw)

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
            email_attachments.append(file_path)
    return email_attachments

def save_attachment(part, dest_dir):
    if bool(part.get_filename()):
        file_path = os.path.join(dest_dir, part.get_filename())
        file_path = urllib.parse.unquote(file_path)
        print(f"save cv to file {file_path}")
        with open(file_path, 'wb') as file:
            file.write(part.get_payload(decode=True))

        return str(file_path)

def to_json_file(metadata, filename, dest_dir):
    print(f"trying to write json to file from with metadata={metadata['uid']}")
    print(f"trying to write json to file={filename}")
    json_obj = json.dumps(metadata, indent=4)
    file_path = file_util.write_to_file(json_obj, filename, dest_dir)
    return file_path
