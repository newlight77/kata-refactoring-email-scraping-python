from infrastructure.email.email_client_hexagonal import EmailClientHexagonal, EmailParserAdapter, EmailScraperAdapter
import pytest
import os
import json
import datetime
from unittest.mock import Mock
from domain.email_scraper_hexagonal import EmailScraperHexagonal, EmailScraperPort, EmailParserPort, FetchedEmail
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
    message.get_all.return_value = ["Kong <newlight77@gmail.com>"]
    message.get.return_value = "subject"
    message.is_multipart.return_value = True

    envelope = Mock()
    envelope.date.strftime.return_value = '2021-06-28_1011'

    raw_emails_with_envelopes = []
    fetched_email = FetchedEmail(1, message, envelope, datetime.datetime.now())
    raw_emails_with_envelopes.append(fetched_email)

    scraper_adapter = Mock()
    parser_adapter = Mock()
    scraper = EmailScraperHexagonal(scraper_adapter, parser_adapter, scraper_config)

    scraper_adapter.fetch_emails.return_value = raw_emails_with_envelopes
    parser_adapter.get_from.return_value = 'newlight77@gmail.com'
    parser_adapter.get_subject.return_value = 'subject'
    parser_adapter.parse_body.return_value = message
    parser_adapter.save_attachments.return_value = ['filename.pdf']
    parser_adapter.to_json_file.return_value = '/tmp/filename.pdf'

    # Act
    result = scraper.scrape()

    # Arrange
    assert result == ['/tmp/filename.pdf']
