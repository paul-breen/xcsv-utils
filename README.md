# xcsv-utils

xcsv-utils is a subpackage of [xcsv](https://github.com/paul-breen/xcsv).  It's main purpose is to provide utilities for working with extended CSV (XCSV) files.

## Install

The package can be installed from PyPI:

```bash
$ pip install xcsv-utils
```

## Using the package

XCSV data can be printed directly, as the data table is a [pandas](https://pandas.pydata.org/docs/index.html) table:

```python
>>> content.data
     time (year) [a]  depth (m)
0               2012      0.575
1               2011      1.125
2               2010      2.225
3               2009      2.825
4               2008      3.508
..               ...        ...
387             1625    132.240
388             1624    132.426
389             1623    132.680
390             1622    132.880
391             1621    133.180

[392 rows x 2 columns]
```

But an XCSV object usually contains an extended header section as well as the data.  Pandas doesn't handle this header, but the XCSV object does.  In addition, the XCSV object parses the data table column headers and makes their content machine-readable.

The `xcsv-utils` subpackage provides simple access and visual inspection of the attributes of an XCSV object - the `metadata` (`header` and `column_headers`) and the `data`.  The main class is `Print`, which provides a formatted, themed view of an XCSV object, and can pretty-print an XCSV file directly from the command line.  This is the purpose of the `xcsv-utils` subpackage.  For example:

```bash
$ python3 -m xcsv.utils example.csv 
id: 1
title: The title
summary: This dataset...
The second summary paragraph.
The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain
authors: A B, C D
latitude: -73.86 (degree_north)
longitude: -65.46 (degree_east)
elevation: 1897 (m a.s.l.)
[a]: 2012 not a complete year
+----+--------------+-------------+
|    |         time |   depth (m) |
|    |   (year) [a] |             |
|----+--------------+-------------|
|  0 |         2012 |       0.575 |
|  1 |         2011 |       1.125 |
|  2 |         2010 |       2.225 |
+----+--------------+-------------+
```

All the colour theming is handled by the [blessed](https://pypi.org/project/blessed/) package, and the data table formatting is handled by the [tabulate](https://pypi.org/project/tabulate/) package.

Note here that we're calling `xcsv-utils` as a *module main*.  As a convenience, this invocation is wrapped as a console script (called `xcsv_print`) when installing the package, hence the following invocation is equivalent:

```bash
$ xcsv_print example.csv
```

A key feature of the CLI, is that the attributes of the XCSV object can be inspected individually.  When called with no options, the header is printed in a themed and formatted way, followed by the data table, which is also themed and formatted.  This is more readable than simply `cat`ing the file.  The modes of the CLI are:

* No options: Print the header, followed by the data table.
* `-H`: Print the header only.
* `-C`: Print the column headers only.  These are printed with a numeric index, so that optionally a subset of columns can be specified when printing the data table.
* `-D`: Print the data table only.  The rows have a leading row index column (as per usual with `pandas` dataframes), so that optionally a subset of rows can be specified when printing the data table.

For example:

```bash
$ xcsv_print example.csv -H
id: 1
title: The title
summary: This dataset...
The second summary paragraph.
The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain
authors: A B, C D
latitude: -73.86 (degree_north)
longitude: -65.46 (degree_east)
elevation: 1897 (m a.s.l.)
[a]: 2012 not a complete year
```

```bash
$ xcsv_print example.csv -C
   0 time (year) [a]
   1 depth (m)
```

```bash
$ xcsv_print example.csv -D
+----+--------------+-------------+
|    |         time |   depth (m) |
|    |   (year) [a] |             |
|----+--------------+-------------|
|  0 |         2012 |       0.575 |
|  1 |         2011 |       1.125 |
|  2 |         2010 |       2.225 |
+----+--------------+-------------+
```

These modes are mutually exclusive.  Each of these options can be combined with the verbose (`-v`) option, to highlight how that attribute was parsed.  For example, when verbosely printing the header, any numeric values with units, and any list items, will be highlighted:

```bash
$ xcsv_print example.csv -Hv
id: 1
title: The title
summary: ['This dataset...', 'The second summary paragraph.', 'The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain']
authors: A B, C D
latitude: value: -73.86, units: degree_north
longitude: value: -65.46, units: degree_east
elevation: value: 1897, units: m a.s.l.
[a]: 2012 not a complete year
```

Similarly for the column headers:

```bash
$ xcsv_print example.csv -Cv
   0 name: time, units: year, notes: a
   1 name: depth, units: m, notes: None
```

and the data table:

```bash
$ xcsv_print example.csv -Dv
+----+---------------+---------------+
|    |    name: time |   name: depth |
|    |   units: year |      units: m |
|    |      notes: a |   notes: None |
|----+---------------+---------------|
|  0 |          2012 |         0.575 |
|  1 |          2011 |         1.125 |
|  2 |          2010 |         2.225 |
+----+---------------+---------------+
```

The data table also has an extra verbose (`-vv`) option whereby it will resolve any table notes to the notes text from the coresponding header item:

```bash
$ xcsv_print example.csv -Dvv
+----+-----------------------------------+---------------+
|    |                        name: time |   name: depth |
|    |                       units: year |      units: m |
|    |   notes: a -> 2012 not a complete |   notes: None |
|    |                              year |               |
|----+-----------------------------------+---------------|
|  0 |                              2012 |         0.575 |
|  1 |                              2011 |         1.125 |
|  2 |                              2010 |         2.225 |
+----+-----------------------------------+---------------+
```

There are further useful options for printing the data table:

* `-c`: Specify a subset of columns to print.  This can be useful when the data table contains a large number of columns.
* `-r`: Similarly, specify a subset of rows to print.
* `--head`: Convenience function.  Print only the first 10 data rows.
* `--tail`: Convenience function.  Print only the last 10 data rows.

All column and row indices are zero-based, and can be ascertained from the `-C` and `-D` options respectively.  They can be specified as comma-separated lists and/or hyphen-separated (inclusive) ranges.

Of course the OS `head` and `tail` (and `less`) commands can be used to limit the output of the table, but doing so will lose the theming.  Moreover though, if the output includes the header, then `head` will apply to the header, and will likely not get as far as showing any of the data table.

For example:

```bash
$ xcsv_print -D --head A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
+----+------------+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+--------------------------+-------------+-----------------------------------------------------------------+
|    | Date       |   A68A_Central_Lat |   A68A_Central_Lon |   A68A_Long_axis_end_Lat1 |   A68A_Long_axis_end_Lon1 |   A68A_Long_axis_end_Lat2 |   A68A_Long_axis_end_Lon2 |   A68A_Long_axis_length |   A68A_Short_axis_length |   A68A_Area | Dimensions_source                                               |
|    |            |     (degree_north) |      (degree_east) |            (degree_north) |             (degree_east) |            (degree_north) |             (degree_east) |                    (km) |                     (km) |       (km2) |                                                                 |
|----+------------+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+--------------------------+-------------+-----------------------------------------------------------------|
|  0 | 2020-09-01 |             -59.42 |             -49.47 |                    -59.63 |                    -50.51 |                    -59.26 |                    -47.98 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  1 | 2020-09-02 |             -59.42 |             -49.49 |                    -59.8  |                    -50.52 |                    -59.11 |                    -48.3  |                 nan     |                  nan     |      nan    | 9999                                                            |
|  2 | 2020-09-03 |             -59.46 |             -49.7  |                    -60.04 |                    -50.18 |                    -58.88 |                    -48.9  |                 149.375 |                   49.875 |     4451.66 | s1a-ew-grd-hh-20200903t223918-20200903t224018-034200-03f92b-001 |
|  3 | 2020-09-04 |             -59.43 |             -49.72 |                    -60.11 |                    -49.77 |                    -58.78 |                    -49.43 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  4 | 2020-09-05 |             -59.45 |             -49.72 |                    -60.06 |                    -49.49 |                    -58.73 |                    -49.72 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  5 | 2020-09-06 |             -59.44 |             -49.66 |                    -59.98 |                    -49.19 |                    -58.69 |                    -50.02 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  6 | 2020-09-07 |             -59.38 |             -49.69 |                    -59.84 |                    -49    |                    -58.69 |                    -50.27 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  7 | 2020-09-08 |             -59.31 |             -49.66 |                    -59.73 |                    -48.85 |                    -58.7  |                    -50.48 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  8 | 2020-09-09 |             -59.29 |             -49.68 |                    -59.72 |                    -48.85 |                    -58.67 |                    -50.47 |                 nan     |                  nan     |      nan    | 9999                                                            |
|  9 | 2020-09-10 |             -59.26 |             -49.7  |                    -59.7  |                    -48.85 |                    -58.64 |                    -50.45 |                 nan     |                  nan     |      nan    | 9999                                                            |
+----+------------+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+--------------------------+-------------+-----------------------------------------------------------------+
$ xcsv_print -C A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
   0 Date
   1 A68A_Central_Lat (degree_north)
   2 A68A_Central_Lon (degree_east)
   3 A68A_Long_axis_end_Lat1 (degree_north)
   4 A68A_Long_axis_end_Lon1 (degree_east)
   5 A68A_Long_axis_end_Lat2 (degree_north)
   6 A68A_Long_axis_end_Lon2 (degree_east)
   7 A68A_Long_axis_length (km)
   8 A68A_Short_axis_length (km)
   9 A68A_Area (km2)
  10 Dimensions_source
$ xcsv_print -D --head -c 0-2 A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
+----+------------+--------------------+--------------------+
|    | Date       |   A68A_Central_Lat |   A68A_Central_Lon |
|    |            |     (degree_north) |      (degree_east) |
|----+------------+--------------------+--------------------|
|  0 | 2020-09-01 |             -59.42 |             -49.47 |
|  1 | 2020-09-02 |             -59.42 |             -49.49 |
|  2 | 2020-09-03 |             -59.46 |             -49.7  |
|  3 | 2020-09-04 |             -59.43 |             -49.72 |
|  4 | 2020-09-05 |             -59.45 |             -49.72 |
|  5 | 2020-09-06 |             -59.44 |             -49.66 |
|  6 | 2020-09-07 |             -59.38 |             -49.69 |
|  7 | 2020-09-08 |             -59.31 |             -49.66 |
|  8 | 2020-09-09 |             -59.29 |             -49.68 |
|  9 | 2020-09-10 |             -59.26 |             -49.7  |
+----+------------+--------------------+--------------------+
$ xcsv_print -D --head -c 0,3-6 A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
+----+------------+---------------------------+---------------------------+---------------------------+---------------------------+
|    | Date       |   A68A_Long_axis_end_Lat1 |   A68A_Long_axis_end_Lon1 |   A68A_Long_axis_end_Lat2 |   A68A_Long_axis_end_Lon2 |
|    |            |            (degree_north) |             (degree_east) |            (degree_north) |             (degree_east) |
|----+------------+---------------------------+---------------------------+---------------------------+---------------------------|
|  0 | 2020-09-01 |                    -59.63 |                    -50.51 |                    -59.26 |                    -47.98 |
|  1 | 2020-09-02 |                    -59.8  |                    -50.52 |                    -59.11 |                    -48.3  |
|  2 | 2020-09-03 |                    -60.04 |                    -50.18 |                    -58.88 |                    -48.9  |
|  3 | 2020-09-04 |                    -60.11 |                    -49.77 |                    -58.78 |                    -49.43 |
|  4 | 2020-09-05 |                    -60.06 |                    -49.49 |                    -58.73 |                    -49.72 |
|  5 | 2020-09-06 |                    -59.98 |                    -49.19 |                    -58.69 |                    -50.02 |
|  6 | 2020-09-07 |                    -59.84 |                    -49    |                    -58.69 |                    -50.27 |
|  7 | 2020-09-08 |                    -59.73 |                    -48.85 |                    -58.7  |                    -50.48 |
|  8 | 2020-09-09 |                    -59.72 |                    -48.85 |                    -58.67 |                    -50.47 |
|  9 | 2020-09-10 |                    -59.7  |                    -48.85 |                    -58.64 |                    -50.45 |
+----+------------+---------------------------+---------------------------+---------------------------+---------------------------+
$ xcsv_print -D --head -c 0,7-8 A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
+----+------------+-------------------------+--------------------------+
|    | Date       |   A68A_Long_axis_length |   A68A_Short_axis_length |
|    |            |                    (km) |                     (km) |
|----+------------+-------------------------+--------------------------|
|  0 | 2020-09-01 |                 nan     |                  nan     |
|  1 | 2020-09-02 |                 nan     |                  nan     |
|  2 | 2020-09-03 |                 149.375 |                   49.875 |
|  3 | 2020-09-04 |                 nan     |                  nan     |
|  4 | 2020-09-05 |                 nan     |                  nan     |
|  5 | 2020-09-06 |                 nan     |                  nan     |
|  6 | 2020-09-07 |                 nan     |                  nan     |
|  7 | 2020-09-08 |                 nan     |                  nan     |
|  8 | 2020-09-09 |                 nan     |                  nan     |
|  9 | 2020-09-10 |                 nan     |                  nan     |
+----+------------+-------------------------+--------------------------+
# Replicate the combined --head and --tail functionality with the -r option
$ xcsv_print -D -c 0,7-8 -r 0-9,218-227 A68_icebergs_positions_and_dimensions_2020-21-A68A.csv
+-----+------------+-------------------------+--------------------------+
|     | Date       |   A68A_Long_axis_length |   A68A_Short_axis_length |
|     |            |                    (km) |                     (km) |
|-----+------------+-------------------------+--------------------------|
|   0 | 2020-09-01 |                 nan     |                  nan     |
|   1 | 2020-09-02 |                 nan     |                  nan     |
|   2 | 2020-09-03 |                 149.375 |                   49.875 |
|   3 | 2020-09-04 |                 nan     |                  nan     |
|   4 | 2020-09-05 |                 nan     |                  nan     |
|   5 | 2020-09-06 |                 nan     |                  nan     |
|   6 | 2020-09-07 |                 nan     |                  nan     |
|   7 | 2020-09-08 |                 nan     |                  nan     |
|   8 | 2020-09-09 |                 nan     |                  nan     |
|   9 | 2020-09-10 |                 nan     |                  nan     |
| 218 | 2021-04-07 |                 nan     |                  nan     |
| 219 | 2021-04-08 |                 nan     |                  nan     |
| 220 | 2021-04-09 |                 nan     |                  nan     |
| 221 | 2021-04-10 |                 nan     |                  nan     |
| 222 | 2021-04-11 |                 nan     |                  nan     |
| 223 | 2021-04-12 |                 nan     |                  nan     |
| 224 | 2021-04-13 |                 nan     |                  nan     |
| 225 | 2021-04-14 |                 nan     |                  nan     |
| 226 | 2021-04-15 |                 nan     |                  nan     |
| 227 | 2021-04-16 |                 nan     |                  nan     |
+-----+------------+-------------------------+--------------------------+
```

In general, the default theme works OK in a dark- or light- background terminal.  The default theme (`light`) assumes a dark background.  If highlighted text is difficult to read on a light background, then specify the `dark` theme instead (`-t dark`).

In addition to using the CLI, the package can be used as a Python library.  The main class is `Print` which provides methods to pretty-print a given dataset (XCSV object):

```python
>>> import xcsv
>>> import xcsv.utils as xu
>>> filename = 'example.csv'
>>> with xcsv.File(filename) as f:
>>>     dataset = f.read()
>>> printer = xu.Print(metadata=dataset.metadata, data=dataset.data)
>>> printer.print_data()
+----+--------------+-------------+
|    |         time |   depth (m) |
|    |   (year) [a] |             |
|----+--------------+-------------|
|  0 |         2012 |       0.575 |
|  1 |         2011 |       1.125 |
|  2 |         2010 |       2.225 |
+----+--------------+-------------+
# To access the formatted and themed string, we can do the following
>>> output = printer.format_data()
>>> output
'+----+----------+---------+\n|    |     \x1b[38;2;190;190;190m\x1b[38;2;190;190;190m\x1b[38;2;190;190;190mtime\x1b[m\x1b[m\x1b[m |   \x1b[38;2;190;190;190m\x1b[38;2;190;190;190m\x1b[38;2;190;190;190mdepth\x1b[m\x1b[m |\n|    |   \x1b[38;2;190;190;190m\x1b[38;2;190;190;190m\x1b[38;2;190;190;190m(year)\x1b[m\x1b[m |     \x1b[38;2;190;190;190m\x1b[38;2;190;190;190m(m)\x1b[m\x1b[m\x1b[m |\n|    |      \x1b[38;2;190;190;190m\x1b[38;2;190;190;190m[a]\x1b[m\x1b[m\x1b[m |         |\n|----+----------+---------|\n|  0 |     2012 |   0.575 |\n|  1 |     2011 |   1.125 |\n|  2 |     2010 |   2.225 |\n+----+----------+---------+'
>>> print(output)
+----+----------+---------+
|    |     time |   depth |
|    |   (year) |     (m) |
|    |      [a] |         |
|----+----------+---------|
|  0 |     2012 |   0.575 |
|  1 |     2011 |   1.125 |
|  2 |     2010 |   2.225 |
+----+----------+---------+
>>> printer.columns = [1]
>>> printer.print_data()
+----+---------+
|    |   depth |
|    |     (m) |
|----+---------|
|  0 |   0.575 |
|  1 |   1.125 |
|  2 |   2.225 |
+----+---------+
>>> printer.print_header()
id: 1
title: The title
summary: This dataset...
The second summary paragraph.
The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain
authors: A B, C D
latitude: -73.86 (degree_north)
longitude: -65.46 (degree_east)
elevation: 1897 (m a.s.l.)
[a]: 2012 not a complete year
>>> printer.verbose = 1
>>> printer.print_header()
id: 1
title: The title
summary: ['This dataset...', 'The second summary paragraph.', 'The third summary paragraph.  Escaped because it contains the delimiter in a URL https://dummy.domain']
authors: A B, C D
latitude: value: -73.86, units: degree_north
longitude: value: -65.46, units: degree_east
elevation: value: 1897, units: m a.s.l.
[a]: 2012 not a complete year
>>> printer.print_column_headers()
   0 name: time, units: year, notes: a
   1 name: depth, units: m, notes: None
```

## Command line usage

Calling the script with the `--help` option will show the following usage:

```bash
$ python3 -m xcsv.utils --help
usage: xcsv_print [-h] [-H] [-C] [-D] [-c COLUMNS] [-r ROWS] [--head]
                  [--tail] [-t {light,dark}] [-v] [-V]
                  in_file

print xcsv file

positional arguments:
  in_file               input XCSV file

optional arguments:
  -h, --help            show this help message and exit
  -H, --header-only     show the extended header section only
  -C, --column-headers-only
                        show the data table column headers only
  -D, --data-only       show the data table only
  -c COLUMNS, --columns COLUMNS
                        columns to include in the data table (specify
                        multiple columns separated by commas and/or as
                        hyphen-separated ranges)
  -r ROWS, --rows ROWS  rows to include in the data table (specify multiple
                        rows separated by commas and/or as hyphen-separated
                        ranges)
  --head                only show the first 10 rows of the data table
  --tail                only show the last 10 rows of the data table
  -t {light,dark}, --theme {light,dark}
                        use the named theme to apply styling to the output
  -v, --verbose         show incrementally verbose output
  -V, --version         show program's version number and exit
```

