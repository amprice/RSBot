import collections
from ast import Assert
import pytest
from unittest.mock import MagicMock, mock_open

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from botenv import getEnvKey

MockObjs = collections.namedtuple("MockObj", ['mock_open', 'mock_file'])

class AnyStringWith(str):
    def __eq__(self, other):
        return self in other
        
@pytest.fixture()
def fix1(monkeypatch):
    mock_file = MagicMock()
    mock_file.readline = MagicMock()
    mock_file.close = MagicMock()
    mock_open = MagicMock(return_value=mock_file)
    monkeypatch.setattr("builtins.open", mock_open)

    m = MockObjs(mock_open, mock_file)
    return m

def test_basicEnvironmentFileReadWithOneMatchingLineTokenArg1(fix1, monkeypatch):
    result = ""
    fix1.mock_file.readline.side_effect = ['TO1KEN=ABCD', 'TOKEN=DEAD']
    result = getEnvKey("TOKEN")
    
    fix1.mock_open.assert_called_once_with(AnyStringWith(".environment"), "r")
    fix1.mock_file.close.assert_called_once()

    assert result == 'DEAD'

def test_basicEnvironmentFileReadWithOneMatchingLineTokenArg2(fix1, monkeypatch):
    result = ""
    fix1.mock_file.readline.side_effect = ['TO1KEN=ABCD', 'TOKEN=DEAD']
    result = getEnvKey("TO1KEN")
    
    fix1.mock_open.assert_called_once_with(AnyStringWith(".environment"), "r")
    fix1.mock_file.close.assert_called_once()

    assert result == 'ABCD'

def test_basicEnvironmentFileReadWithNoMatchingTOKENLine(fix1, monkeypatch):
    result = ""

    fix1.mock_file.readline.side_effect = ['TO1KEN=ABCD', '']

    result = getEnvKey("TOKEN")
    
    fix1.mock_open.assert_called_once_with(AnyStringWith(".environment"), "r")
    fix1.mock_file.close.assert_called_once()

    assert result == ''
