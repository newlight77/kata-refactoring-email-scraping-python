import pytest
from shared.collections_util.dict_util import DefDictToObject

@pytest.mark.shared
def test_encrypt_message():
    # Arrange :
    data = {
        'key1': 'value1',
        'key2': 'value2',
    }

    # Act :
    data_object = DefDictToObject(data)

    # Assert :
    assert data_object.key1 == 'value1'
    assert data_object.key2 == 'value2'
