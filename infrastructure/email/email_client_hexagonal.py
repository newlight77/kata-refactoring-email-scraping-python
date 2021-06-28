import email
from imapclient import IMAPClient
from domain.email_scraper_hexagonal import EmailScraperPort
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

        raw_emails_with_envelopes = []
        for (uid, raw_message), (uid, raw_envelop) in zip(raw_emails, raw_envelopes):
            logger.info(f"fetch emails: yield UID={uid}")
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
