###############################################################################
# Project: Extended CSV common file format
# Purpose: Classes of utilities for working with an extended CSV file
# Author:  Paul M. Breen
# Date:    2023-05-06
###############################################################################

__version__ = '0.1.0'

import textwrap

import pandas as pd
from tabulate import tabulate
from blessed import Terminal

import xcsv

_term = Terminal()

def _reset():
    return '\033[m' if _term.is_a_tty else ''

class Print(xcsv.XCSV):
    """
    Class for printing extended CSV objects
    """

    # For some reason, when using _term.normal to reset styling, means that
    # tabulate messes up the column header widths, hence using reset
    THEMES = {
      'light': {
        'default': _term.white, 'reset': _reset(), 'normal': _term.normal,
        'k1': _term.blue, 'v1': _term.gray,
        'k2': _term.green, 'v2': _term.gray,
      },
      'dark': {
        'default': _term.black, 'reset': _reset(), 'normal': _term.normal,
        'k1': _term.blue, 'v1': _term.dimgray,
        'k2': _term.green, 'v2': _term.dimgray,
      }
    }

    DEFAULTS = {
      'verbose': False,
      'columns': None,
      'rows': None,
      'theme': THEMES['light'],
      'kv_delimiter': ':',
      'list_delimiter': ', ',
      'end': '\n',
      'column_header_index_padding': 4,
      'wrap_opts': {'width': 10, 'break_long_words': False},
      'notes_wrap_opts': {'width': 20, 'break_long_words': False},
      'table_opts': {'headers': 'keys', 'tablefmt': 'psql', 'showindex': True}
    }

    def __init__(self, metadata=None, data=None):
        """
        Constructor

        :param metadata: The extended CSV metadata
        :type metadata: dict
        :param data: The extended CSV data
        :type data: pandas.dataframe
        """

        super().__init__(metadata=metadata, data=data)

        for key in self.DEFAULTS:
            setattr(self, key, self.DEFAULTS[key])

    def configure_pandas_full_display(self):
        """
        Configure pandas for display

        Ensure pandas doesn't trunctate dataframes when printing out
        """

        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option("display.expand_frame_repr", False)

    def wrap_column_text(self, text, wrap_opts=None):
        """
        Wrap text in data table column headers from the xcsv object

        If wrap_opts are not defined, then the configured self.wrap_opts
        are used.

        :param text: The column header text
        :type text: str
        :param wrap_opts: The kwarg options to textwrap.wrap()
        :type wrap_opts: dict
        :returns: The wrapped text
        :rtype: str
        """

        if not wrap_opts:
            wrap_opts = self.wrap_opts

        wrapped = self.end.join(textwrap.wrap(text, **wrap_opts))

        return wrapped

    def format_wrapped_text_parts(self, text, formatter):
        """
        Individually format the parts of the given wrapped text

        We have to surround each part of the wrapped text with the
        theme, otherwise tabulate messes up the column headers.

        :param text: The wrapped text
        :type text: str
        :param formatter: The formatter function to pass each part to
        :type formatter: function
        :returns: The wrapped text, with each part formatted
        :rtype: str
        """

        parts = []

        for part in text.split(self.end):
            parts.append(formatter(part))

        text = self.end.join(parts)

        return text

    def format_header_item(self, item, kv_delimiter=':', list_delimiter=', '):
        """
        Format the given header item

        The header item can be from the extended header section or from a
        column header.

        :param kv_delimiter: The delimiter to separate the key/value of a
        single component of the item
        :type kv_delimiter: str
        :param list_delimiter: The delimiter to separate mulitiple components
        of the item (e.g., if item is a dict or list)
        :type list_delimiter: str
        :returns: The formatted header item
        :rtype: str
        """

        if isinstance(item, dict):
            parts = []

            for ikey in item:
                parts.append(f"{self.theme['k2']}{ikey + kv_delimiter} {self.theme['v2']}{str(item[ikey])}{self.theme['reset']}")

            line = list_delimiter.join(parts)
        elif isinstance(item, list):
            parts = []

            for element in item:
                parts.append(f"{self.theme['k2']}'{self.theme['v2']}{element}{self.theme['k2']}'")

            line = f"{self.theme['k2']}[{list_delimiter.join(parts)}{self.theme['k2']}]{self.theme['reset']}"
        else:
            line = f"{self.theme['v2']}{str(item)}{self.theme['reset']}"

        return line

    def expand_column_header(self, key, list_delimiter='\n'):
        """
        Expand the data table column header for the given key

        This expands the column header into the components of the dict,
        suitably highlighted according to the theme.

        If running in extra verbose mode, then any column notes are looked up
        from the extended header section and incorporated.

        :param key: The column header key
        :type key: str
        :param list_delimiter: The delimiter to separate mulitiple components
        of the column header dict
        :type list_delimiter: str
        :returns: The formatted column header
        :rtype: str
        """

        section = 'column_headers'

        item = self.get_metadata_item(key, section=section)
        line = self.format_header_item(item, list_delimiter=list_delimiter)

        if self.verbose > 1:
            notes = self.get_notes_for_column_header(key)

            if notes is not None:
                notes = self.wrap_column_text(notes, wrap_opts=self.notes_wrap_opts)
                notes = self.format_wrapped_text_parts(notes, self.format_header_item)
                line = f"{line} {self.theme['k2']}-> {self.theme['v2']}{notes}{self.theme['reset']}"

        return line

    def expand_column_headers(self):
        """
        Expand the data table column headers from the xcsv object

        This renames the data table columns with their expanded
        representation, as returned by expand_column_header().

        :returns: The column map used to do the renaming
        :rtype: dict
        """

        col_map = {}
        section = 'column_headers'

        for key in self.metadata[section]:
            col_map[key] = self.expand_column_header(key)

        self.data.rename(columns=col_map, inplace=True)

        return col_map

    def wrap_column_headers(self):
        """
        Wrap the data table column headers from the xcsv object

        This renames the data table columns with their wrapped
        representation, as returned by wrap_column_text().

        :returns: The column map used to do the renaming
        :rtype: dict
        """

        col_map = {}

        for key in self.data.columns:
            text = self.wrap_column_text(key)
            text = self.format_wrapped_text_parts(text, self.format_header_item)
            col_map[key] = text

        self.data.rename(columns=col_map, inplace=True)

        return col_map

    def format_header(self):
        """
        Format the extended header section from the xcsv object

        If running in verbose mode, then compound header items are expanded.

        :returns: The formatted extended header section
        :rtype: str
        """

        lines = []
        section = 'header'
        list_delimiter = f"{self.theme['k2']}{self.list_delimiter}"

        for key in self.metadata[section]:
            if self.verbose:
                item = self.get_metadata_item(key, section=section)
                value = self.format_header_item(item, list_delimiter=list_delimiter)
            else:
                value = self.get_metadata_item_string(key, section=section)

            line = f"{self.theme['k1']}{key + self.kv_delimiter} {self.theme['v1']}{value}{self.theme['reset']}"
            lines.append(line)

        header = self.end.join(lines)

        return header

    def format_column_headers(self):
        """
        Format the data table column headers from the xcsv object

        If running in verbose mode, then the table column headers are expanded.

        :returns: The formatted column headers
        :rtype: str
        """

        lines = []
        section = 'column_headers'
        list_delimiter = f"{self.theme['k2']}{self.list_delimiter}"

        for i, key in enumerate(self.metadata[section]):
            if self.verbose:
                line = self.expand_column_header(key, list_delimiter=list_delimiter)
            else:
                line = f"{self.theme['v2']}{key}{self.theme['reset']}"

            # Prepend zero-based column number, useful for subsetting columns
            lines.append(f"{self.theme['reset']}{i: {self.column_header_index_padding}} " + line)

        column_headers = self.end.join(lines)

        return column_headers

    def format_data(self):
        """
        Format the data table from the xcsv object

        If running in verbose mode, then the table column headers are expanded.

        If self.columns or self.rows have been set, then these are used to
        subset the table.

        :returns: The formatted data table
        :rtype: str
        """

        if self.verbose:
            self.expand_column_headers()
        else:
            self.wrap_column_headers()

        data = self.data

        if self.columns:
            data = data.iloc[:, self.columns]

        if self.rows:
            data = data.iloc[self.rows, :]

        return tabulate(data, **self.table_opts)

    def reset_theme(self):
        """
        Reset any theme styling back to the terminal default

        :returns: The terminal reset code
        :rtype: str
        """

        return f"{self.theme['reset']}"

    def print_header(self):
        """
        Print the extended header section from the xcsv object
        """

        print(self.format_header() + self.reset_theme())

    def print_column_headers(self):
        """
        Print the data table column headers from the xcsv object
        """

        print(self.format_column_headers() + self.reset_theme())

    def print_data(self):
        """
        Print the data table from the xcsv object
        """

        print(self.format_data() + self.reset_theme())

