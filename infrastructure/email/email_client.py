import email
from email.header import decode_header
import html2text
from imapclient import IMAPClient
import json
import os
import urllib.parse
from shared.file_util import file_util
from shared.decorators.pipe import pipe

class EmailClient:
    def __init__(self, config):
        self.imap = None
        self.config = config

    def connect(self):
        self.imap = IMAPClient(self.config.host)
        self.imap.login(self.config.email, self.config.password)
        return self.imap

    def scrape(self):
        if type(self.imap) is not IMAPClient:
            raise ValueError("client must be of type IMAPClient")

        all_emails_summary = {}
        for uid, raw_message, raw_envelop in self.fetch_emails():
            envelop = raw_envelop[b'ENVELOPE']
            date = envelop.date.strftime('%Y%m%d_%H%M')

            message = email.message_from_bytes(raw_message[b'RFC822'])
            email_from = get_from(message)
            email_subject = get_subject(message).strip()
            print(f"processing: email UID={uid} from {email_from} @ {envelop.date} -> {email_subject}")
            all_emails_summary[f'{email_from}-{date}-{uid}'] = parse_message(message, self.config.attachment_dir)

        return all_emails_summary

    def fetch_emails(self):
        self.imap.select_folder(self.config.folder, readonly=False)
        messages = self.imap.search([self.config.search_key_words])
        envelopes = self.imap.fetch(messages, ['ENVELOPE']).items()
        emails = self.imap.fetch(messages, 'RFC822').items()
        for (uid, raw_message), (uid, raw_envelop) in zip(emails, envelopes):
            yield (uid, raw_message, raw_envelop)


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
    return subject.strip()


def parse_message(message, attachment_dir):
    if message.is_multipart():
        return parse_multipart_message(message, attachment_dir)
    return parse_single_part(message)


def parse_single_part(raw_message):
    email_data = {}
    if raw_message.get_content_type() == 'text/html':
        email_data["Plain_HTML"] = html2text.html2text(raw_message.get_payload())
        email_data["HTML"] = raw_message.get_payload()

    if raw_message.get_content_type() == 'text/plain':
        email_data["Plain_Text"] = raw_message.get_payload()

    return email_data


def parse_multipart_message(email_message, attachment_dir):
    email_data = {}
    attachments = []
    for part in email_message.walk():
        if bool(part.get_filename()):
            file_path = save_attachment(part, attachment_dir)
            attachments.append(file_path)

        email_data = parse_single_part(part)

    email_data['attachments'] = attachments
    return email_data


def save_attachment(part, dest_dir):
    if bool(part.get_filename()):
        file_path = os.path.join(dest_dir, part.get_filename())
        file_path = urllib.parse.unquote(file_path)
        print(f"save cv to file {file_path}")
        with open(file_path, 'wb') as file:
            file.write(part.get_payload(decode=True))

    return str(file_path)


@pipe
def summary_to_json_file(summary, dest_dir):
    file_list = []
    for key in summary.keys():
        try:
            json_obj = json.dumps(summary[key], indent=4)
            file_path = file_util.write_to_file(json_obj, f"{key}.json", dest_dir)
            file_list.append(file_path)
        except ValueError:
            continue

    return file_list
