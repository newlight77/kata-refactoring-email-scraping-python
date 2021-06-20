import email
from email.header import decode_header
import html2text
from imapclient import IMAPClient
import json
import os
import urllib.parse
from shared.file_util import file_util
from shared.decorators.pipe import Pipe

class EmailClientPipe:
    def __init__(self, config):
        self.imap = None
        self.config = config

    def connect(self):
        self.imap = IMAPClient(self.config.host)
        self.imap.login(self.config.email, self.config.password)
        return self

    def scrape(self):
        print(f'scraping by {self} with imap={self.imap}')
        self.fetch_emails() \
            | parse_emails() \
            | parse_emails_body() \
            | parse_email_attachments(self.config.attachment_dir) \
            | summary_to_json_file(self.config.attachment_dir)

    def fetch_emails(self):
        print(f"fetch emails with imap={self.imap}")
        self.imap.select_folder(self.config.folder, readonly=False)
        messages = self.imap.search([self.config.search_key_words])
        raw_envelopes = self.imap.fetch(messages, ['ENVELOPE']).items()
        raw_emails = self.imap.fetch(messages, 'RFC822').items()

        raw_emails_with_envelopes = []
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            print(f"fetch emails: yield UID={uid}")
            raw_emails_with_envelopes.append((uid, raw_message, raw_envelop))
        return raw_emails_with_envelopes

@Pipe
def parse_emails(raw_emails_with_envelopes):
    print(f"parse emails with raw_emails_with_envelopes")
    messages = []
    for (uid, raw_message, raw_envelop) in raw_emails_with_envelopes:
        envelop = raw_envelop[b'ENVELOPE']
        date = envelop.date.strftime('%Y%m%d_%H%M')

        message = email.message_from_bytes(raw_message[b'RFC822'])
        email_from = get_from(message)
        email_subject = get_subject(message).strip()
        print(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")

        metadata = {
            'uid': uid,
            'from': email_from,
            'subject': email_subject,
            'date': date
        }

        messages.append((uid, metadata, message))
    return messages

@Pipe
def parse_emails_body(parsed_messages):
    print(f"parse emails body with parsed_messages")
    messages = []
    for (uid, metadata, message) in parsed_messages:

        print(f"parsing email body for UID={uid}")

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
                email_body["HTML"] = part.get_payload()

            if message.get_content_type() == 'text/plain':
                email_body["Plain_Text"] = message.get_payload()

        metadata['body'] = email_body

        messages.append((uid, metadata, message))
    return messages

@Pipe
def parse_email_attachments(parsed_messages, attachment_dir):
    print(f"parse emails attachments with parsed_messages")
    messages = []
    for (uid, metadata, message) in parsed_messages:
        print(f"parsing email attachments for UID={uid}")

        email_attachments = []
        if message.is_multipart():
            for part in message.walk():
                if bool(part.get_filename()):
                    file_path = save_attachment(part, attachment_dir)
                    email_attachments.append(file_path)

        metadata['attachments'] = email_attachments

        messages.append((uid, metadata, message))
    return messages

@Pipe
def summary_to_json_file(parsed_messages, dest_dir):
    print(f"write summary to json file with metadatas")
    file_list = []
    for (uid, metadata, message) in parsed_messages:
        try:
            print(f"json from with metadata={metadata['uid']}")
            json_obj = json.dumps(metadata, indent=4)
            filename = f"{metadata['from']}-{metadata['date']}-{metadata['uid']}.json"
            file_path = file_util.write_to_file(json_obj, filename, dest_dir)
            file_list.append(file_path)
        except ValueError:
            print(f"an error occured while dumping metadata into json for message uid={metadata['uid']}")
            continue

    return file_list


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


def save_attachment(part, dest_dir):
    if bool(part.get_filename()):
        file_path = os.path.join(dest_dir, part.get_filename())
        file_path = urllib.parse.unquote(file_path)
        print(f"save cv to file {file_path}")
        with open(file_path, 'wb') as file:
            file.write(part.get_payload(decode=True))

    return str(file_path)
