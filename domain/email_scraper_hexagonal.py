from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)


class EmailScraperPort:
    def connect(self):
        pass

    def scrape(self):
        pass


class EmailParserPort:
    def get_from(self, message):
        pass

    def get_subject(self, message):
        pass

    def parse_body(self, message):
        pass

    def save_attachments(self, message, attachment_dir):
        pass

    def to_json_file(self, metadata, filename, dest_dir):
        pass


class EmailScraperHexagonal:
    def __init__(self, scraperAdapter: EmailScraperPort, emailParser: EmailParserPort, config):
        self.config = config
        self.adapter = scraperAdapter
        self.emailParser = emailParser

    def connect(self):
        return self.adapter.connect()

    def scrape(self):
        raw_emails_with_envelopes = self.adapter.scrape()
        parsed_messages = self.parse_emails(raw_emails_with_envelopes)
        parsed_messages = self.parse_emails_body(parsed_messages)
        print('self.config', self.config)
        parsed_messages = self.parse_email_attachments(parsed_messages, self.config.attachment_dir)
        self.summary_to_json_file(parsed_messages, self.config.attachment_dir)

    def parse_emails(self, raw_emails_with_envelopes):
        logger.debug("parse emails with raw_emails_with_envelopes")
        messages = []
        for (uid, message, envelop) in raw_emails_with_envelopes:
            date = envelop.date.strftime('%Y%m%d_%H%M')

            email_from = self.emailParser.get_from(message)
            email_subject = self.emailParser.get_subject(message).strip()
            logger.info(f"processing: email UID={uid} from {email_from} @ {date} -> {email_subject}")

            metadata = {
                'uid': uid,
                'from': email_from,
                'subject': email_subject,
                'date': date
            }

            messages.append((uid, metadata, message))
        return messages

    def parse_emails_body(self, parsed_messages):
        logger.debug("parse emails body with parsed_messages")
        messages = []
        for (uid, metadata, message) in parsed_messages:
            logger.debug(f"parsing email body for UID={uid}")
            metadata['body'] = self.emailParser.parse_body(message)
            messages.append((uid, metadata, message))
        return messages

    def parse_email_attachments(self, parsed_messages, attachment_dir):
        logger.debug("parse emails attachments with parsed_messages")
        messages = []
        for (uid, metadata, message) in parsed_messages:
            logger.debug(f"parsing email attachments for UID={uid}")
            email_attachments = self.emailParser.save_attachments(message, attachment_dir)
            metadata['attachments'] = email_attachments
            messages.append((uid, metadata, message))
        return messages

    def summary_to_json_file(self, parsed_messages, dest_dir):
        logger.info("write summary to json file with metadatas")
        file_list = []
        for (uid, metadata, message) in parsed_messages:
            try:
                filename = f"{metadata['from']}-{metadata['date']}-{metadata['uid']}.json"
                file_path = self.emailParser.to_json_file(metadata, filename, dest_dir)
                file_list.append(file_path)
            except ValueError:
                logger.error(f"an error occured while dumping metadata into json for message uid={metadata['uid']}")
                continue

        return file_list
