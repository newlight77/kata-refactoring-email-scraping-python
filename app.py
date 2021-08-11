import logging
from config import config
from app import app_email_listener, app_email_hexagonal, app_email_pipe

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"running the email scraper on {config.env}")
    # app_email_listener.run()
    app_email_hexagonal.run()
    # app_email_pipe.run()
