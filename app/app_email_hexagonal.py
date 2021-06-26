from imapclient import IMAPClient
from config import config
from domain.email_scraper_hexagonal import EmailScraperHexagonal
from infrastructure.email.email_client_hexagonal import EmailClientHexagonal, EmailScraperAdapter
from shared.collections_util import dict_util


class EmailScrapeHandler():
    def __init__(self, scraper: EmailScraperHexagonal, adapter: EmailScraperAdapter, config):
        self.scraper = scraper
        self.adapter = adapter
        self.config = config

    def connect(self):
        return self.scraper.connect()


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
    listen(client, config)


def listen(client: EmailClientHexagonal, config):
    imap = client.imap

    if type(imap) is not IMAPClient:
        raise ValueError("imap must be of type IMAPClient")

    scraperAdapter = EmailScraperAdapter(client, config)
    scraper = EmailScraperHexagonal(scraperAdapter, config)
    handler = EmailScrapeHandler(scraper, scraperAdapter, config)

    handler.scrape()

    imap.idle()
    print("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            print("imap sent:", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                handler.scrape()

                imap.idle()  # idling
    except ValueError as ve:
        print(f"error: {ve}")
    except KeyboardInterrupt as ki:
        print(f"error: {ki}")
    finally:
        print("terminating the app")
        imap.idle_done()
        imap.logout()
