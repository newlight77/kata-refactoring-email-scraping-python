from infrastructure.email.email_parser import get_from, get_subject, parse_body, save_attachments
from domain.fetched_email import FetchedEmail
import email
from imapclient import IMAPClient
from shared.json_util.json_util import to_json_file
from domain.email_scraper_hexagonal import EmailParserPort, EmailScraperPort
from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)


class EmailClientHexagonal:
    def __init__(self, imap, config):
        self.imap = imap
        self.config = config

    def connect(self):
        self.imap = self.imap or IMAPClient(self.config.host)
        self.imap.login(self.config.email, self.config.password)
        return self

    def fetch_emails(self):
        logger.debug(f"fetch emails with imap={self.imap}")
        self.imap.select_folder(self.config.folder, readonly=False)
        messages = self.imap.search(self.config.search_key_words)
        raw_envelopes = self.imap.fetch(messages, ['ENVELOPE']).items()
        raw_emails = self.imap.fetch(messages, 'RFC822').items()

        emails_with_envelopes = []
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            logger.info(f"fetch emails: yield UID={uid}")
            message = email.message_from_bytes(raw_message[b'RFC822'])
            envelop = raw_envelop[b'ENVELOPE']
            date = envelop.date.strftime('%Y%m%d_%H%M')
            emails_with_envelopes.append(FetchedEmail(uid, message, envelop, date))

        return emails_with_envelopes


class EmailScraperAdapter(EmailScraperPort):
    # pylint: disable=too-many-arguments
    def __init__(self, email_client: EmailClientHexagonal, config):
        self.client = email_client
        self.config = config

    def connect(self):
        return self.client.connect()

    def fetch_emails(self):
        return self.client.fetch_emails()


class EmailParserAdapter(EmailParserPort):

    def get_from(self, email_message):
        return get_from(email_message)

    def get_subject(self, email_message):
        return get_subject(email_message)

    def parse_body(self, message):
        return parse_body(message)

    def save_attachments(self, message, dest_dir):
        email_attachments = []
        if message.is_multipart():
            for part in message.walk():
                file_path = save_attachments(part, dest_dir)
                email_attachments.append(file_path)
        return email_attachments

    def to_json_file(self, metadata, filename, dest_dir):
        return to_json_file(metadata, filename, dest_dir)
