"""
    Interface of scraper
"""

from infrastructure.email.email_client_hexagonal import EmailClientHexagonal
from domain.email_scraper_port import EmailScraperPort

class EmailScraperAdapter(EmailScraperPort):
    # pylint: disable=too-many-arguments
    def __init__(self, emailClient: EmailClientHexagonal, config):
        self.client = emailClient
        self.config = config

    def connect(self):
        return self.client.connect()

    def scrape(self):
        return self.client.fetch_emails()
