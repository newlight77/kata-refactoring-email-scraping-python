from imapclient import IMAPClient
from config import config
from domain.email_scraper_hexagonal import EmailScraperHexagonal
from domain.email_scraper_uc_hexagonal import EmailScraperUseCaseHexagonal
from infrastructure.email.email_client_hexagonal import EmailClientHexagonal, EmailScraperAdapter, EmailParserAdapter, EmailParser
from shared.collections_util import dict_util
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
    client = EmailClientHexagonal(imap, scraper_config)
    client = client.connect()

    scraper_adapter = EmailScraperAdapter(client, scraper_config)
    parser = EmailParser()
    parser_adapter = EmailParserAdapter(parser)
    scraper = EmailScraperHexagonal(scraper_adapter, parser_adapter, scraper_config)
    usecase = EmailScraperUseCaseHexagonal(scraper_config, scraper)

    listen(client, usecase, scraper_config)


def listen(client: EmailClientHexagonal, handler: EmailScraperUseCaseHexagonal, config):
    imap = client.imap

    # if type(imap) is not IMAPClient:
    #     raise ValueError("imap must be of type IMAPClient")

    handler.scrape()

    imap.idle()
    logger.info("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            logger.info("imap sent: %s", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                handler.scrape()

                imap.idle()  # idling
    except ValueError as ve:
        logger.error(f"error: {ve}")
    except KeyboardInterrupt as ki:
        logger.error(f"error: {ki}")
    finally:
        logger.info("terminating the app")
        imap.idle_done()
        imap.logout()
