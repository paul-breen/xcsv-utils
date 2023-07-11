import os

import pytest

import xcsv
import xcsv.utils as xu

base = os.path.dirname(__file__)

def test_version():
    assert xu.__version__ == '0.1.0'

@pytest.fixture
def short_test_datasets():
    in_files = [f'{base}/data/short-test-data-{n}.csv' for n in range(1, 3)]
    datasets = []

    for in_file in in_files:
        with xcsv.File(in_file) as f:
            datasets.append(f.read())

    return datasets

def test_Print_unconfigured_instantiation():
    f = xu.Print()

@pytest.mark.parametrize(['text','wrap_opts', 'end', 'expected'], [
('time (year) [a]', None, None, 'time\n(year) [a]'),
('123 567 90123 567 90', None, None, '123 567\n90123 567\n90'),
('1234567890123 567 90', None, None, '1234567890123\n567 90'),
('1234567890 23 567 90', None, None, '1234567890\n23 567 90'),
('1234567890 23 567 9012345', None, None, '1234567890\n23 567\n9012345'),
('1234567890123 567 9012345', None, None, '1234567890123\n567\n9012345'),
('1234567890123 567 9012345', {'width': 10, 'break_long_words': True}, None, '1234567890\n123 567\n9012345'),
('1234567890123 567 9012345', {'width': 12, 'break_long_words': False}, None, '1234567890123\n567 9012345'),
('123 567 90123 567 90', None, '|', '123 567|90123 567|90'),
('123 567 90123 567 90', None, '<br/>', '123 567<br/>90123 567<br/>90'),
])
def test_wrap_column_text(text, wrap_opts, end, expected):
    f = xu.Print()

    if end is not None:
        f.end = end

    actual = f.wrap_column_text(text, wrap_opts=wrap_opts)
    assert actual == expected

@pytest.mark.parametrize(['text','formatter', 'expected'], [
('time\n(year) [a]', 'format_header_item', 'time\n(year) [a]'),
('123 567\n90123 567\n90', 'format_header_item', '123 567\n90123 567\n90'),
('1234567890123\n567 90', 'format_header_item', '1234567890123\n567 90'),
('1234567890\n23 567 90', 'format_header_item', '1234567890\n23 567 90'),
('1234567890\n23 567\n9012345', 'format_header_item', '1234567890\n23 567\n9012345'),
('1234567890123\n567\n9012345', 'format_header_item', '1234567890123\n567\n9012345'),
('1234567890\n123 567\n9012345', 'format_header_item', '1234567890\n123 567\n9012345'),
('1234567890123\n567 9012345', 'format_header_item', '1234567890123\n567 9012345'),
])
def test_format_wrapped_text_parts(text, formatter, expected):
    f = xu.Print()
    actual = f.format_wrapped_text_parts(text, getattr(f, formatter))
    assert actual == expected

@pytest.mark.parametrize(['item', 'expected'], [
('time (year) [a]', 'time (year) [a]'),
({'name': 'time', 'units': 'year', 'notes': 'a'}, 'name: time, units: year, notes: a'),
({'name': 'depth', 'units': 'm', 'notes': None}, 'name: depth, units: m, notes: None'),
({'name': 'qc', 'units': None, 'notes': 'b'}, 'name: qc, units: None, notes: b'),
({'name': 'event_marker', 'units': None, 'notes': None}, 'name: event_marker, units: None, notes: None'),
(['This dataset...', 'The second summary paragraph.', 'The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain'], "['This dataset...', 'The second summary paragraph.', 'The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain']"),
])
def test_format_header_item(item, expected):
    f = xu.Print()
    actual = f.format_header_item(item)
    assert actual == expected

@pytest.mark.parametrize(['item', 'kv_delimiter', 'list_delimiter', 'expected'], [
({'name': 'time', 'units': 'year', 'notes': 'a'}, '->', ',', 'name-> time,units-> year,notes-> a'),
({'name': 'time', 'units': 'year', 'notes': 'a'}, '=', '; ', 'name= time; units= year; notes= a'),
])
def test_format_header_item_custom_delimters(item, kv_delimiter, list_delimiter, expected):
    f = xu.Print()
    actual = f.format_header_item(item, kv_delimiter=kv_delimiter, list_delimiter=list_delimiter)
    assert actual == expected

@pytest.mark.parametrize(['dataset_index', 'key', 'expected'], [
(0, 'time (year) [a]', 'name: time\nunits: year\nnotes: a'),
(0, 'depth (m)', 'name: depth\nunits: m\nnotes: None'),
(1, 'qc [b]', 'name: qc\nunits: None\nnotes: b'),
(1, 'event_marker', 'name: event_marker\nunits: None\nnotes: None'),
])
def test_expand_column_header(dataset_index, key, expected, short_test_datasets):
    dataset = short_test_datasets[dataset_index]
    f = xu.Print(metadata=dataset.metadata, data=dataset.data)
    actual = f.expand_column_header(key)
    assert actual == expected

@pytest.mark.parametrize(['dataset_index', 'key', 'expected'], [
(0, 'time (year) [a]', 'name: time\nunits: year\nnotes: a -> 2012 not a complete\nyear'),
(0, 'depth (m)', 'name: depth\nunits: m\nnotes: None'),
(1, 'qc [b]', 'name: qc\nunits: None\nnotes: b -> 0 = non-QC\'d age, 1\n= QC\'d age'),
(1, 'event_marker', 'name: event_marker\nunits: None\nnotes: None'),
])
def test_expand_column_header_extra_verbose(dataset_index, key, expected, short_test_datasets):
    """
    When verbose > 1, any notes references are resolved from the
    corresponding notes label in the extended header section
    """

    dataset = short_test_datasets[dataset_index]
    f = xu.Print(metadata=dataset.metadata, data=dataset.data)
    f.verbose = 2
    actual = f.expand_column_header(key)
    assert actual == expected

