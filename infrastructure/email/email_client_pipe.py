import email
from email.header import decode_header
import html2text
from imapclient import IMAPClient
import json
import os
import urllib.parse
from shared.file_util import file_util
from shared.decorators.pipe import pipe

class EmailClientPipe:
    def __init__(self, config):
        self.imap = None
        self.config = config

    def connect(self):
        self.imap = IMAPClient(self.config.host)
        self.imap.login(self.config.email, self.config.password)
        return self.imap
    
    @pipe
    def scrape(self):
        print(f'scraping by {self}')
        return self >> self.fetch_emails() \
            >> self.parse_emails() #\
            # >> self.parse_mail_body() \
            #>> self.parse_email_attachments()

    @pipe
    def fetch_emails(self):
        print(f'fetch emails by {self}')
        self.imap.select_folder(self.config.folder, readonly=False)
        messages = self.imap.search([self.config.search_key_words])
        raw_envelopes = self.imap.fetch(messages, ['ENVELOPE']).items()
        raw_emails = self.imap.fetch(messages, 'RFC822').items()
        return self, raw_emails, raw_envelopes

    @pipe
    def parse_emails(self, raw_emails, raw_envelopes):
        print(f'parse emails by {self}')
        emails_summary = {}
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            envelop = raw_envelop[b'ENVELOPE']
            date = envelop.date.strftime('%Y%m%d_%H%M')

            message = email.message_from_bytes(raw_message[b'RFC822'])
            email_from = get_from(message)
            email_subject = get_subject(message).strip()
            print(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")

            emails_summary[uid] = {
                'uid': uid,
                'from': email_from,
                'subject': email_subject,
                'date': date
            }
            
        return self, raw_emails, emails_summary

    @pipe
    def parse_emails_body(self, raw_emails, emails_summary):
        emails_summary = emails_summary or {}
        for (uid, raw_message) in raw_emails:

            message = email.message_from_bytes(raw_message[b'RFC822'])
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
                if raw_message.get_content_type() == 'text/html':
                    email_body["Plain_HTML"] = html2text.html2text(raw_message.get_payload())
                    email_body["HTML"] = part.get_payload()

                if raw_message.get_content_type() == 'text/plain':
                    email_body["Plain_Text"] = raw_message.get_payload()

            emails_summary[uid].body = email_body
            
        return self, emails_summary

    @pipe
    def parse_email_attachments(self, raw_emails, emails_summary):
        emails_summary = emails_summary or {}
        for (uid, raw_message) in raw_emails:
            message = email.message_from_bytes(raw_message[b'RFC822'])
            print(f"parsing email attachments for UID={uid}")
            
            email_attachments = []
            if message.is_multipart():
                for part in message.walk():
                    if bool(part.get_filename()):
                        file_path = save_attachment(part, self.config.attachment_dir)
                        email_attachments.append(file_path)

            emails_summary[uid].attachments = email_attachments

        return emails_summary


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


@pipe
def summary_to_json_file(summary, dest_dir):
    file_list = []
    print(f'summary={summary}')
    for key in summary.keys():
        try:
            json_obj = json.dumps([key], indent=4)
            filename = f"{key}.json"
            file_path = file_util.write_to_file(json_obj, filename, dest_dir)
            file_list.append(file_path)
        except ValueError:
            continue

    return file_list
