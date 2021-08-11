from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)


class FetchedEmail:
    def __init__(self, uid, message, envelop, date):
        self.uid = uid
        self.message = message
        self.envelop = envelop
        self.date = date
        self.metadata = None


class EmailScraperPort:
    def fetch_emails(self):
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
    def __init__(self, scraper_adapter: EmailScraperPort, email_parser: EmailParserPort, config):
        self.config = config
        self.adapter = scraper_adapter
        self.email_parser = email_parser

    def scrape(self):
        emails_with_envelopes = self.adapter.fetch_emails()
        emails_with_metadata = self.parse_emails(emails_with_envelopes)
        emails_with_body = self.parse_emails_body(emails_with_metadata)
        print('self.config', self.config)
        emails_with_attachments = self.parse_email_attachments(emails_with_body, self.config.attachment_dir)
        return self.summary_to_json_file(emails_with_attachments, self.config.attachment_dir)

    def parse_emails(self, emails_with_envelopes):
        logger.debug("parse emails with envelopes")
        emails_with_metadata = []
        for email in emails_with_envelopes:
            if type(email) == FetchedEmail:
                date = email.envelop.date
                email_from = self.email_parser.get_from(email.message)
                email_subject = self.email_parser.get_subject(email.message).strip()
                logger.info(f"processing: email UID={email.uid} from {email_from} @ {date} -> {email_subject}")

                email.metadata = {
                    'uid': email.uid,
                    'from': email_from,
                    'subject': email_subject,
                    'date': date
                }

                emails_with_metadata.append(email)
        return emails_with_metadata

    def parse_emails_body(self, emails_with_metadata):
        logger.debug("parse emails body with parsed_messages %s", emails_with_metadata)
        emails_with_body = []
        for email in emails_with_metadata:
            logger.debug(f"parsing email body for UID={email.uid}")
            email.metadata['body'] = self.email_parser.parse_body(email.message)
            emails_with_body.append(email)
        return emails_with_body

    def parse_email_attachments(self, emails_with_body, attachment_dir):
        logger.debug("parse emails attachments with parsed_messages %s", emails_with_body)
        emails_with_attachments = []
        for email in emails_with_body:
            logger.debug(f"parsing email attachments for UID={email.uid}")
            email_attachments = self.email_parser.save_attachments(email.message, attachment_dir)
            email.metadata['attachments'] = email_attachments
            emails_with_attachments.append(email)
        return emails_with_attachments

    def summary_to_json_file(self, emails_with_body, dest_dir):
        logger.info("write summary to json file with metadatas %s", emails_with_body)
        file_list = []
        for email in emails_with_body:
            try:
                logger.debug('metadata %s', email.metadata)
                filename = f"{email.metadata['from']}-{email.metadata['date']}-{email.metadata['uid']}.json"
                file_path = self.email_parser.to_json_file(email.metadata, filename, dest_dir)
                file_list.append(file_path)
            except ValueError as error:
                logger.error(f"an error occured while dumping metadata into json for message uid={email.metadata['uid']} with error={error}")
                continue

        return file_list
