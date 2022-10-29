import collections
from ast import Assert
from unittest.result import failfast
import pytest
from unittest.mock import MagicMock, mock_open

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

import botversion

MockObjs = collections.namedtuple("TestMocks", ['mock_open', 'mock_file'])

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

def test_readingVaildHash(fix1):
    fix1.mock_file.readline.side_effect = ['DUMMY_HASH', '']
    result = botversion.getGitHash()
    assert result == 'DUMMY_HASH'

def test_readingHashFileNotFound(fix1):
    botversion.githashFilename = 'invalid_filename'
    result = botversion.getGitHash()
    assert result == ''

def test_getBotVersionWithHash(fix1):
    botversion.SW_ID = "V1.0"
    botversion.githashFilename = '.githash'
    fix1.mock_file.readline.side_effect = ['DUMMY_HASH', '']
    result = botversion.getVersion()
    assert result == 'V1.0-DUMMY_HASH'

def test_getBotVersionWithoutHash(fix1):
    botversion.SW_ID = "V1.0"
    botversion.githashFilename = 'invalid_filename'
    result = botversion.getVersion()
    assert result == 'V1.0'
