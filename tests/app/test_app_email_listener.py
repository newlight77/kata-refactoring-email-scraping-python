from shared.collections_util import dict_util
from app.app_email_listener import EmailScraper, listen
from imapclient import IMAPClient
import pytest
from unittest import mock

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
    return mock.Mock()


def test_should_listener_start_listening_with_no_data(imap, scraper_config):
    # Arrange
    # pylint: disable=no-member
    imap.select_folder(scraper_config.folder, readonly=False).return_value = None

    message = {}
    message[b'RFC822'] = bytes('email2', 'utf-8')

    messages = {}
    imap.search.return_value = messages

    class Items():
        def items(self):
            print('fetch', messages)
            return []

    imap.fetch.return_value = Items()

    times = 0

    def idle():
        nonlocal times
        if (times > 0):
            raise KeyboardInterrupt
        times += 1

    imap.idle = idle

    scraper = EmailScraper()

    # Act
    listen(imap, scraper, scraper_config)

    # Assert
    imap.logout.assert_called()
