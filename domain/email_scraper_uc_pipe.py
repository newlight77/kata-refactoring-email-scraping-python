from domain.email_scraper_pipe import parse_emails, parse_emails_body, parse_email_attachments, summary_to_json_file
from shared.decorators.pipe import Pipe
from config import logger, config

logger = logger.logger(__name__, config.LOG_LEVEL)

@Pipe
def scrape(data, config):
    return data \
        | parse_emails() \
        | parse_emails_body() \
        | parse_email_attachments(config.attachment_dir) \
        | summary_to_json_file(config.attachment_dir)
