from config import config
from shared.collections_util import dict_util
from infrastructure.email.email_client_pipe import EmailClientPipe
from app.app_email_pipe import listen
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
def email_client_pipe(imap, scraper_config):
    return EmailClientPipe(imap, scraper_config)


@pytest.mark.pipe
def test_should_connect_imap_pipe(scraper_config):
    # Arrange
    client = EmailClientPipe(Mock(), scraper_config)

    # Act
    client = client.connect()

    # Assert
    client.imap.login.assert_called_once_with('test@example.com', 'test-password')


@pytest.mark.pipe
def test_should_pipe_start_listening_with_no_data(imap, scraper_config):
    # Arrange
    # pylint: disable=no-member
    client = EmailClientPipe(imap, scraper_config)
    imap.select_folder(scraper_config.folder, readonly=False).return_value = None

    message = {}
    message[b'RFC822'] = bytes('email2', 'utf-8')

    messages = {}
    imap.search.return_value = messages

    def items():
        return []

    imap.fetch.return_value = Mock(items=items)

    times = 0

    def idle():
        nonlocal times
        if (times > 0):
            raise KeyboardInterrupt
        times += 1

    imap.idle = idle

    # Act
    client | listen(scraper_config)

    # Assert
    client.imap.logout.assert_called()
