from config import logger, config
from domain.email_scraper_hexagonal import EmailScraperHexagonal
logger = logger.logger(__name__, config.LOG_LEVEL)


class EmailScraperUseCaseHexagonal:
    def __init__(self, config, email_scraper: EmailScraperHexagonal):
        self.config = config
        self.scraper = email_scraper

    def scrape(self):
        raw_emails_with_envelopes = self.scraper.scrape()
        parsed_messages = self.scraper.parse_emails(raw_emails_with_envelopes)
        parsed_messages = self.scraper.parse_emails_body(parsed_messages)
        print('self.config', self.scraper.config)
        parsed_messages = self.scraper.parse_email_attachments(parsed_messages, self.config.attachment_dir)
        return self.scraper.summary_to_json_file(parsed_messages, self.config.attachment_dir)
