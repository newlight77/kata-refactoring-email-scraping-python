import pytest
from shared.decorators.pipe import pipe, Pipe


@pytest.mark.shared
def test_should_pipe_functions_using_rrshift():

    # Arrange
    @pipe
    def select(data1, arg):
        print(f'select data={data1}')
        return data1[arg]

    @pipe
    def merge(data1, data2):
        print(f'merge data1={data1} and data2={data2}')
        return data1 + data2

    data = {'one': [1, 2, 3, 4, 4], 'two': [4, 3, 2, 1, 3]}

    # Act
    result = data >> select('one') >> merge(data['two'])

    # Assert
    assert result == [1, 2, 3, 4, 4, 4, 3, 2, 1, 3]


@pytest.mark.shared
def test_should_pipe_functions_using_ror():

    # Arrange
    @Pipe
    def select(data1, arg):
        print(f'select data={data1}')
        return data1[arg]

    @Pipe
    def merge(data1, data2):
        print(f'merge data1={data1} and data2={data2}')
        return data1 + data2

    data = {'one': [1, 2, 3, 4, 4], 'two': [4, 3, 2, 1, 3]}

    # Act
    result = data | select('one') | merge(data['two'])

    # Assert
    assert result == [1, 2, 3, 4, 4, 4, 3, 2, 1, 3]
