from domain.email_scraper_port import EmailScraperPort
from infrastructure.email.email_client_pipe import get_from, get_subject, parse_body, save_attachments, to_json_file

class EmailScraperHexagonal:
    def __init__(self, scraperAdapter: EmailScraperPort, config):
        self.config = config
        self.adapter = scraperAdapter

    def connect(self):
        return self.adapter.connect()

    def scrape(self):
        raw_emails_with_envelopes = self.adapter.scrape()
        parsed_messages = self.parse_emails(raw_emails_with_envelopes)
        parsed_messages = self.parse_emails_body(parsed_messages)
        parsed_messages = self.parse_email_attachments(parsed_messages, self.config.attachment_dir)
        self.summary_to_json_file(parsed_messages, self.config.attachment_dir)

    def parse_emails(self, raw_emails_with_envelopes):
        print("parse emails with raw_emails_with_envelopes")
        messages = []
        for (uid, message, envelop) in raw_emails_with_envelopes:
            date = envelop.date.strftime('%Y%m%d_%H%M')

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

    def parse_emails_body(self, parsed_messages):
        print("parse emails body with parsed_messages")
        messages = []
        for (uid, metadata, message) in parsed_messages:
            print(f"parsing email body for UID={uid}")
            metadata['body'] = parse_body(message)
            messages.append((uid, metadata, message))
        return messages

    def parse_email_attachments(self, parsed_messages, attachment_dir):
        print("parse emails attachments with parsed_messages")
        messages = []
        for (uid, metadata, message) in parsed_messages:
            print(f"parsing email attachments for UID={uid}")
            email_attachments = save_attachments(message, attachment_dir)
            metadata['attachments'] = email_attachments
            messages.append((uid, metadata, message))
        return messages

    def summary_to_json_file(self, parsed_messages, dest_dir):
        print("write summary to json file with metadatas")
        file_list = []
        for (uid, metadata, message) in parsed_messages:
            try:
                filename = f"{metadata['from']}-{metadata['date']}-{metadata['uid']}.json"
                file_path = to_json_file(metadata, filename, dest_dir)
                file_list.append(file_path)
            except ValueError:
                print(f"an error occured while dumping metadata into json for message uid={metadata['uid']}")
                continue

        return file_list
