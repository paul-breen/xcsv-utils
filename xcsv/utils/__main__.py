###############################################################################
# Project: Extended CSV common file format
# Purpose: Classes of utilities for working with an extended CSV file
# Author:  Paul M. Breen
# Date:    2023-05-06
###############################################################################

import argparse

import xcsv
import xcsv.utils as xu

INDENT = 4

DEF_OPT_SEPARATOR = ','
DEF_OPT_RANGE_SEPARATOR = '-'

HEAD_N_ROWS = 10
TAIL_N_ROWS = HEAD_N_ROWS

def str_range_list_to_list(x, item_sep=DEF_OPT_SEPARATOR, range_sep=DEF_OPT_RANGE_SEPARATOR):
    """
    Convert a string range list to a list

    For example, given '1,2,3,8-12,14,17', return [1,2,3,8,9,10,11,12,14,17]

    :param x: String, possibly including a range specification
    :type x: str
    :param item_sep: The separator between items in the string
    :type item_sep: str
    :param range_sep: The separator between range end-points in the string
    :type range_sep: str
    :returns: The fully actualised list
    :rtype: list
    """

    y = []
    items = x.split(item_sep)

    for i in items:
        if range_sep in i:
            lim = i.split(range_sep)
            y.extend([r for r in range(int(lim[0]), int(lim[1])+1)])
        else:
            y.append(i)

    return y

def str_range_arg_to_list(x, item_sep=DEF_OPT_SEPARATOR, range_sep=DEF_OPT_RANGE_SEPARATOR):
    """
    Convert a range command line argument to a list

    For example, given '1,2,3,8-12,14,17', return [1,2,3,8,9,10,11,12,14,17]

    :param x: String, possibly including a range specification
    :type x: str
    :param item_sep: The separator between items in the string
    :type item_sep: str
    :param range_sep: The separator between range end-points in the string
    :type range_sep: str
    :returns: The fully actualised list
    :rtype: list
    """

    if not isinstance(x, range):
        # Option can have multiple delimited values
        if item_sep in str(x) or range_sep in str(x):
            x = str_range_list_to_list(x)

        # Value must be a list, so we don't iterate over digits in a string
        if not isinstance(x, list):
            x = [x]

        # Ensure value is an int list after all processing
        x = [int(i) for i in x]

    return x

def parse_cmdln():
    """
    Parse the command line

    :returns: An object containing the command line arguments and options
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(description='print xcsv file', formatter_class=argparse.RawDescriptionHelpFormatter, prog='xcsv_print')
    parser.add_argument('in_file', help='input XCSV file')

    parser.add_argument('-H', '--header-only', help='show the extended header section only', action='store_true', default=False)
    parser.add_argument('-C', '--column-headers-only', help='show the data table column headers only', action='store_true', default=False)
    parser.add_argument('-D', '--data-only', help='show the data table only', action='store_true', default=False)

    parser.add_argument('-c', '--columns', help='columns to include in the data table (specify multiple columns separated by commas and/or as hyphen-separated ranges)', type=str)
    parser.add_argument('-r', '--rows', help='rows to include in the data table (specify multiple rows separated by commas and/or as hyphen-separated ranges)', type=str)

    parser.add_argument('--head', help=f"only show the first {HEAD_N_ROWS} rows of the data table", dest='rows', action='store_const', const=range(0,HEAD_N_ROWS))
    parser.add_argument('--tail', help=f"only show the last {TAIL_N_ROWS} rows of the data table", dest='rows', action='store_const', const=range(-TAIL_N_ROWS,0))

    parser.add_argument('-t', '--theme', help='use the named theme to apply styling to the output', type=str, choices=list(xu.Print.THEMES.keys()))

    parser.add_argument('-v', '--verbose', help='show incrementally verbose output', action='count')
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {xu.__version__}")
    args = parser.parse_args()

    if args.columns:
        args.columns = str_range_arg_to_list(args.columns)

    if args.rows:
        args.rows = str_range_arg_to_list(args.rows)

    return args

def get_dataset(filename):
    """
    Read the XCSV dataset from the given file

    :param filenam: The filename to be read in
    :type filename: str
    :returns: The contents of the given file as an XCSV object
    :rtype: XCSV
    """

    dataset = None

    with xcsv.File(filename) as f:
        dataset = f.read()

    return dataset

def main():
    """
    Main function
    """

    args = parse_cmdln()
    dataset = get_dataset(args.in_file)
    printer = xu.Print(metadata=dataset.metadata, data=dataset.data)

    printer.verbose = args.verbose
    printer.columns = args.columns
    printer.rows = args.rows

    if args.theme:
        printer.theme = xu.Print.THEMES[args.theme]

    if args.header_only:
        printer.print_header()
    elif args.column_headers_only:
        printer.print_column_headers()
    elif args.data_only:
        printer.print_data()
    else:
        printer.print_header()
        printer.print_data()

if __name__ == '__main__':
    main()

