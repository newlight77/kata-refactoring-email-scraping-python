from imapclient import IMAPClient
from config import config
from domain.email_scraper_hexagonal import EmailScraperHexagonal
from infrastructure.email.email_client_hexagonal import EmailClientHexagonal, EmailScraperAdapter
from shared.collections_util.dict_util import DefDictToObject

def run():
    # pylint: disable=no-member
    scraper_config = DefDictToObject({
        'host': config.EMAIL_HOST,
        'email': config.EMAIL,
        'password': config.EMAIL_PASSWORD,
        'folder': config.FOLDER,
        'attachment_dir': config.ATTACHMENTS_DIR,
        'timeout': 15,
        'read_post_action': config.EMAIL_READ_POST_ACTION,
        'search_key_words': config.EMAIL_SEARCH_KEYWORDS.split(',')
    })

    emailClient = EmailClientHexagonal(scraper_config)
    scraperAdapter = EmailScraperAdapter(emailClient, scraper_config)
    scraper = EmailScraperHexagonal(scraperAdapter, scraper_config)
    handler = EmailScrapeHandler(scraper, scraperAdapter, scraper_config)
    handler.connect()
    handler.listen()

class EmailScrapeHandler():
    def __init__(self, scraper: EmailScraperHexagonal, adapter: EmailScraperAdapter, config):
        self.scraper = scraper
        self.adapter = adapter
        self.imap = None
        self.config = config

    def connect(self):
        self.imap = self.scraper.connect()

    def listen(self):
        imap = self.imap
        config = self.config

        if type(imap) is not IMAPClient:
            raise ValueError("imap must be of type IMAPClient")

        self.scraper.scrape()

        imap.idle()
        print("Connection is now in IDLE mode.")

        try:
            while (True):
                responses = imap.idle_check(config.timeout)
                print("imap sent:", responses if responses else "nothing")

                if (responses):
                    imap.idle_done()  # Suspend the idling

                    self.scraper.scrape()

                    imap.idle()  # idling
        except ValueError as ve:
            print(f"error: {ve}")
        except KeyboardInterrupt as ki:
            print(f"error: {ki}")
        finally:
            print("terminating the app")
            imap.idle_done()
            imap.logout()
