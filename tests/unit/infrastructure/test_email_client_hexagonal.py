from infrastructure.email.email_client_hexagonal import EmailParser
import pytest
import os
import json
import datetime
from unittest.mock import Mock
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
    if(os.path.isfile("/tmp/UnknownEmail-2021-06-28_1011-1.json")):
        os.remove("/tmp/UnknownEmail-2021-06-28_1011-1.json")


def test_should_retrieve_sender_from_message_with_hexagonal():
    # Arrange
    message = Mock()
    message.get_all.return_value = ["Kong <newlight77@gmail.com>"]

    # Act
    result = EmailParser().get_from(message)

    # Arrange
    assert result == 'newlight77@gmail.com'

def test_should_retrieve_email_subject_from_message_with_hexagonal():
    # Arrange
    message = Mock()
    message.get.return_value = "subject"

    # Act
    result = EmailParser().get_subject(message)

    # Arrange
    assert result == 'subject'

def test_should_parse_email_body_from_message_with_hexagonal():
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
    message.is_multipart.return_value = True

    # Act
    result = EmailParser().parse_body(message)

    # Arrange
    assert result['Plain_Text'] == 'email content'

def test_should_save_attachment_from_message_with_hexagonal():
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
    message.is_multipart.return_value = True

    # Act
    result = EmailParser().save_attachments(message, '/tmp/')

    # Arrange
    assert result == ['/tmp/filename.pdf']

def test_should_save_to_json_email_parsing_summary_with_hexagonal():
    # Arrange
    metadata = {}
    metadata['uid'] = 1
    metadata['from'] = 'newlight77@gmail.com'
    metadata['subject'] = 'subject'
    metadata['date'] = '2021-06-28_1011'
    metadata['body'] = {'Plain_Text': 'email content'}
    metadata['attachments'] = ['/tmp/filename.pdf']

    # Act
    result = EmailParser().to_json_file(metadata, 'UnknownEmail-2021-06-28_1011-1.json', '/tmp/')

    # Arrange
    assert result == '/tmp/UnknownEmail-2021-06-28_1011-1.json'

    with open("/tmp/UnknownEmail-2021-06-28_1011-1.json", 'r') as file:
        data = file.read()
    obj = json.loads(data)

    assert obj == {
        'uid': 1,
        'from': 'newlight77@gmail.com',
        'subject': 'subject',
        'date': '2021-06-28_1011',
        'body': {'Plain_Text': 'email content'},
        'attachments': ['/tmp/filename.pdf']
    }
