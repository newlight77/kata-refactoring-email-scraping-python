import json
import pytest
import os
from shared.json_util.json_util import to_json_file
from shared.collections_util.dict_util import DefDictToObject


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup
    file = "/tmp/UnknownEmail-2021-06-28_1011-1.json"

    yield  # this is where the testing happens

    # Teardown
    if(os.path.isfile(file)):
        os.remove(file)


@pytest.mark.shared
def test_should_save_to_json_email_parsing_summary_with_hexagonal():
    # Arrange
    data = {}
    data['uid'] = 1
    data['from'] = 'newlight77@gmail.com'
    data['subject'] = 'subject'
    data['date'] = '2021-06-28_1011'
    data['body'] = {'Plain_Text': 'email content'}
    data['attachments'] = ['/tmp/filename.pdf']

    # Act
    result = to_json_file(data, 'UnknownEmail-2021-06-28_1011-1.json', '/tmp/')

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
