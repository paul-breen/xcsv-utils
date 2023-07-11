import os
import importlib

import pytest

import xcsv.utils as xu

base = os.path.dirname(__file__)

# The state to determine whether blessed.Terminal is writing to a TTY is
# done on package import, hence we reload so we can patch a known state

def test__reset_is_tty(mocker, capsys):
    mocker.patch('os.isatty', return_value=True)
    importlib.reload(xu)

    assert xu._term.is_a_tty is True

    expected = '\033[m\n'
    print(xu._reset())
    captured = capsys.readouterr()
    assert captured.out == expected

def test__reset_is_not_tty(mocker, capsys):
    mocker.patch('os.isatty', return_value=False)
    importlib.reload(xu)

    assert xu._term.is_a_tty is False

    expected = '\n'
    print(xu._reset())
    captured = capsys.readouterr()
    assert captured.out == expected

