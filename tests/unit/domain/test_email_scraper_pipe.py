import pytest
import json
import os
from unittest.mock import Mock
from domain import email_scraper_pipe as scraper
from shared.collections_util import dict_util

@pytest.fixture
def scraper_config():
    # pylint: disable=no-member
    return dict_util.DefDictToObject({
        'host': 'impa.example.com',
        'email': 'test@example.com',
        'password': 'test-password',
        'folder': 'inbox',
        'attachment_dir': '/tmp',
        'timeout': 1,
        'read_post_action': {'action': 'move', 'move_dest': 'cv_folder'},
        'search_key_words': 'FROM,jw@baeldung.com,SINCE,31-May-2021'
    })

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup

    yield  # this is where the testing happens

    # Teardown
    if(os.path.isfile("/tmp/filename.pdf")):
        os.remove("/tmp/filename.pdf")
    if(os.path.isfile("/tmp/i-2021-06-28_1011-1.json")):
        os.remove("/tmp/i-2021-06-28_1011-1.json")


def test_should_scrape_email_with_attachment_by_mocking_data_with_pipe_impl(scraper_config):
    # Arrange
    part1 = Mock()
    part1.get_content_type.return_value = 'text/plain'
    part1.get_payload.return_value = 'email content'
    part1.get_filename.return_value = None
    part2 = Mock()
    part2.get_payload.return_value = 'email content'.encode('utf-8')
    part2.get_filename.return_value = 'filename.pdf'

    message = Mock()
    message.walk.return_value = [part1, part2]
    message.get_all.return_value = "ipaddresss"
    message.get.return_value = "subject"
    message.is_multipart.return_value = True

    envelope = Mock()
    envelope.date.strftime.return_value = '2021-06-28_1011'

    raw_emails_with_envelopes = []
    raw_emails_with_envelopes.append((1, message, envelope))

    # Act
    raw_emails_with_envelopes | scraper.scrape(scraper_config)

    # Assert
    assert os.path.isfile("/tmp/filename.pdf")
    assert os.path.isfile("/tmp/i-2021-06-28_1011-1.json")

    with open("/tmp/i-2021-06-28_1011-1.json", 'r') as file:
        data = file.read()
    obj = json.loads(data)
    print("json content: " + str(obj))
