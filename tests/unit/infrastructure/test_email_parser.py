from infrastructure.email.email_parser import get_from, get_subject, parse_body, save_attachments
import pytest
import os
from unittest.mock import Mock


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


@pytest.mark.hexagonal
def test_should_retrieve_sender_from_message_with_hexagonal():
    # Arrange
    message = Mock()
    message.get_all.return_value = ["Kong <newlight77@gmail.com>"]

    # Act
    result = get_from(message)

    # Arrange
    assert result == 'newlight77@gmail.com'

@pytest.mark.hexagonal
def test_should_retrieve_email_subject_from_message_with_hexagonal():
    # Arrange
    message = Mock()
    message.get.return_value = "subject"

    # Act
    result = get_subject(message)

    # Arrange
    assert result == 'subject'

@pytest.mark.hexagonal
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
    result = parse_body(message)

    # Arrange
    assert result['Plain_Text'] == 'email content'

@pytest.mark.hexagonal
def test_should_save_attachment_from_message_with_hexagonal():
    # Arrange
    part1 = Mock()
    part1.get_content_type.return_value = 'text/plain'
    part1.get_payload.return_value = 'email content'
    part1.get_filename.return_value = None
    part2 = Mock()
    part2.get_payload.return_value = 'email content'  # .encode('utf-8')
    part2.get_filename.return_value = 'filename.pdf'

    message = Mock()
    message.walk.return_value = [part1, part2]
    message.is_multipart.return_value = True

    # Act
    result = save_attachments(message, '/tmp/')

    # Arrange
    assert result == ['/tmp/filename.pdf']
