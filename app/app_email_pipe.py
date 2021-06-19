from email.header import decode_header
from infrastructure.email.email_scraper import EmailScraper, summary_to_json_file
from imapclient import IMAPClient
from config import config
from shared.collections_util import dict_util
from shared.decorators.pipe import pipe

def run():
    """
    Running the Email scraper based on Email-listeneer
    """

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

    scraper_config >> connect() >> listen(scraper_config)

@pipe
def connect(config):
    server = IMAPClient(config.host)
    server.login(config.email, config.password)
    return server


@pipe
def listen(server, config):
    
    if type(server) is not IMAPClient:
        raise ValueError("server must be of type IMAPClient")

    server.idle()
    print("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = server.idle_check(config.timeout)
            print("Server sent:", responses if responses else "nothing")

            if (responses):
                server.idle_done()  # Suspend the idling

                scrape(server, config)

                server.idle()  # idling
    except KeyboardInterrupt:
        print("treminating the app")
    finally:
        server.idle_done()
        server.logout()


def scrape(server, config):
    scraper = EmailScraper(server, config)
    scraper.scrape() >> summary_to_json_file(config.attachment_dir)
