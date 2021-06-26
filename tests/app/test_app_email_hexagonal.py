from shared.collections_util import dict_util
from app.app_email_hexagonal import EmailScrapeHandler
from domain.email_scraper_hexagonal import EmailScraperHexagonal
from infrastructure.email.email_client_hexagonal import EmailClientHexagonal, EmailScraperAdapter
from app.app_email_hexagonal import listen
from imapclient import IMAPClient
import pytest
from unittest.mock import Mock

@pytest.fixture
def scraper_config():
    # pylint: disable=no-member
    return dict_util.DefDictToObject({
        'host': 'impa.example.com',
        'email': 'test@example.com',
        'password': 'test-password',
        'folder': 'inbox',
        'attachment_dir': 'sv',
        'timeout': 1,
        'read_post_action': {'action': 'move', 'move_dest': 'cv_folder'},
        'search_key_words': 'FROM,jw@baeldung.com,SINCE,31-May-2021'
    })

@pytest.fixture
def imap():
    return Mock()

@pytest.fixture
def email_client_hexagonal(imap, scraper_config):
    return EmailClientHexagonal(imap, scraper_config)


def test_should_connect_imap_hexagonal(scraper_config):
    # Arrange
    client = EmailClientHexagonal(Mock(), scraper_config)

    # Act
    client = client.connect()

    # Assert
    #assert client.imap.login is None
    client.imap.login.assert_called_once_with('test@example.com', 'test-password')


def test_should_start_listening_hexagonal(imap, scraper_config):
    # Arrange
    # pylint: disable=no-member
    client = EmailClientHexagonal(imap, scraper_config)
    imap.select_folder(scraper_config.folder, readonly=False).return_value = None

    message = {}
    message[b'RFC822'] = bytes('email2', 'utf-8')
    #items = {'11': [(1, message)]}

    messages = {}
    imap.search.return_value = messages
    imap.fetch.return_value = messages

    def items(messages, arg):
        print('fetch', messages, arg)
        return [(1, message), (1, message)]

    imap.fetch.items = items

    times = 0

    def idle():
        nonlocal times
        if (times > 0):
            raise KeyboardInterrupt
        times += 1

    imap.idle = idle

    scraperAdapter = EmailScraperAdapter(client, scraper_config)
    scraper = EmailScraperHexagonal(scraperAdapter, scraper_config)
    handler = EmailScrapeHandler(scraper, scraperAdapter, scraper_config)

    # Act
    listen(client, handler, scraper_config)

    # Assert
    client.imap.logout.assert_called()
