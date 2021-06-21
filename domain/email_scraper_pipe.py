from infrastructure.email.email_client_pipe import *
from domain.email_scraper_port import EmailScraperPort

class EmailScraperPipe:
    def __init__(self, client: EmailClientPipe, config):
        self.config = config
        self.client = client

    def scrape(self):
        self.client.fetch_emails() \
            | parse_emails() \
            | parse_emails_body() \
            | parse_email_attachments(self.config.attachment_dir) \
            | summary_to_json_file(self.config.attachment_dir)
