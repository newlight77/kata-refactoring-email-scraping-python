from infrastructure.email.email_client_pipe import EmailClientPipe
from domain.email_scraper_pipe import scrape

from imapclient import IMAPClient
from config import config
from shared.collections_util import dict_util
from shared.decorators.pipe import Pipe
from config import logger

logger = logger.logger(__name__, config.LOG_LEVEL)

def run():
    # pylint: disable=no-member
    scraper_config = dict_util.DefDictToObject({
        'host': config.EMAIL_HOST,
        'email': config.EMAIL,
        'password': config.EMAIL_PASSWORD,
        'folder': config.FOLDER,
        'attachment_dir': config.ATTACHMENTS_DIR,
        'timeout': 30,
        'read_post_action': config.EMAIL_READ_POST_ACTION,
        'search_key_words': config.EMAIL_SEARCH_KEYWORDS.split(',')
    })

    imap = IMAPClient(scraper_config.host)
    client = EmailClientPipe(imap, scraper_config)
    client.connect() \
        | listen(scraper_config)


@Pipe
def listen(client: EmailClientPipe, config):
    imap = client.imap

    # if type(imap) is not IMAPClient:
    #     raise ValueError("imap must be of type IMAPClient")

    client.fetch_emails() | scrape(config)
    logger.info(f"imap = {imap}")

    imap.idle()
    logger.info("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            logger.info("imap sent: %s", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                client.fetch_emails() | scrape(config)

                imap.idle()  # idling
    except ValueError as ve:
        logger.error(f"error: {ve}")
    except KeyboardInterrupt as ki:
        logger.warning(f"error KeyboardInterrupt: {ki}")
    finally:
        logger.info("terminating the app")
        imap.idle_done()
        imap.logout()

    return client
