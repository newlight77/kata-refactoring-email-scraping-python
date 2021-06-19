from infrastructure.email.email_client import EmailClient, summary_to_json_file
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
    client = EmailClient(config)
    client.connect()
    return client


@pipe
def listen(client, config):
    imap = client.imap

    if type(imap) is not IMAPClient:
        raise ValueError("client must be of type IMAPClient")

    imap.idle()
    print("Connection is now in IDLE mode.")

    try:
        while (True):
            responses = imap.idle_check(config.timeout)
            print("Email client sent:", responses if responses else "nothing")

            if (responses):
                imap.idle_done()  # Suspend the idling

                scrape(client, config)

                imap.idle()  # idling
    except ValueError as ve:
        print(f"error: {ve}")
    except KeyboardInterrupt as ki:
        print(f"error: {ki}")
    finally:
        print("terminating the app")
        imap.idle_done()
        imap.logout()


def scrape(client: EmailClient, config):
    client.scrape() \
        >> summary_to_json_file(config.attachment_dir)
