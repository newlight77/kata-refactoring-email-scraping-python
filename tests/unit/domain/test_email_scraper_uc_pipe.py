from datetime import datetime
from domain.fetched_email import FetchedEmail
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
    attachement_filepath = "/tmp/filename.pdf"
    summary_filepath = "/tmp/newlight77@gmail.com-2021-06-28 10:11:00-1.json"

    yield  # this is where the testing happens

    # Teardown
    if(os.path.isfile(attachement_filepath)):
        os.remove(attachement_filepath)
    if(os.path.isfile(summary_filepath)):
        os.remove(summary_filepath)


@pytest.mark.pipe
def test_should_scrape_email_with_attachment_by_mocking_data_with_pipe_impl(scraper_config):
    # Arrange
    part1 = Mock()
    part1.get_content_type.return_value = 'text/plain'
    part1.get_payload.return_value = 'email content'
    part1.get_filename.return_value = None
    part2 = Mock()
    part2.get_payload.return_value = 'email content'#.encode('utf-8')
    part2.get_filename.return_value = '/tmp/filename.pdf'

    message = Mock()
    message.walk.return_value = [part1, part2]
    message.get_all.return_value = ["Kong <newlight77@gmail.com>"]
    message.get.return_value = "subject"
    message.is_multipart.return_value = True

    envelope = Mock()
    #envelope.date.strftime.return_value = '2021-06-28_1011'
    envelope.date = datetime.fromisoformat('2021-06-28T10:11:00')

    raw_emails_with_envelopes = []
    fetched_email = FetchedEmail(1, message, envelope, datetime.now())
    raw_emails_with_envelopes.append(fetched_email)

    # Act
    result = raw_emails_with_envelopes | scraper.scrape(scraper_config)

    # Assert
    assert result == ['/tmp/newlight77@gmail.com-2021-06-28 10:11:00-1.json']

    assert os.path.isfile("/tmp/filename.pdf")
    assert os.path.isfile("/tmp/newlight77@gmail.com-2021-06-28 10:11:00-1.json")

    with open("/tmp/newlight77@gmail.com-2021-06-28 10:11:00-1.json", 'r') as file:
        data = file.read()

    json_object = json.loads(data)

    assert json_object == {
        'uid': 1,
        'from': 'newlight77@gmail.com',
        'subject': 'subject',
        'date': '2021-06-28 10:11:00',
        'body': {'Plain_Text': 'email content'},
        'attachments': ['/tmp/filename.pdf']
    }
