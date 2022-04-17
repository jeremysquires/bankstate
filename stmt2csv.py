#!/usr/bin/env python

"""

stmt2csv.py converts text copied from bank statements in PDF format
	into a CSV format that can be imported into home finance software

Copyright (C) 2017 Jeremy Squires <jms@mailforce.net>

License: https://opensource.org/licenses/MIT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

See README.md for more information

"""

import fileinput
import time

line_idx = 0  # line index
has_tabs = False  # whether this file is tab delimitted

num_columns = 0  # static count of columns (and sections)

block = []  # store rows of a block (array of arrays)
section_idx = 0  # section index
row_idx = 0  # row index within a section


def date_convert(inDate):
    """Takes a date string in Jan 14 2017 format (with . or , in there)
    and Returns a date in YYYY-MM-DD format"""
    # remove periods and commas, if any ... inconsistent in output
    inDate = inDate.translate("".maketrans("", "", ".,"))
    # note %e does not work in strptime!! py documentation fail
    time_tuple = time.strptime(inDate, "%b %d %Y")
    return time.strftime("%Y-%m-%d", time_tuple)


def serialize_block(inBlock):
    """Take an array of arrays, join each with ',' and output to stdout"""
    for row in inBlock:
        print(",".join(row))


# loop through all lines in a file
for line in fileinput.input():
    # pass print(line) # stubs
    line = line.strip("\n\r")  # remove CRLF but no other whitespace
    if line_idx == 0:
        # get header fields, numbers
        # if it contains tabs, then RBC MC
        if line.find("\t") > -1:
            has_tabs = True
            # print("Has tabs")
            # substitute commas for tabs
            # WARN: Assumes column header values do not contain commas, tabs or double quotes
            num_columns = line.count("\t") + 1  # count of columns
            line = line.replace("\t", ",")
            print(line)
        else:
            has_tabs = False
            # print("Has spaces")
            line = line.strip(" ")  # do not count spaces at ends
            # substitute commas for spaces
            num_columns = line.count(" ") + 1  # count of columns
            # WARN: Assumes column header values do not contain commas, spaces or double quotes
            # TODO: handle quote surrounded column header values
            line = line.replace(" ", ",")
            print(line)
    elif has_tabs:
        # TODO: handle other tab delimited files ...
        # process the RBC lines one at a time
        # print("RBC line %d" % (line_idx))
        # split by tab
        linelist = line.split("\t")
        # fix the fields
        linelist[0] = date_convert(linelist[0])
        linelist[1] = date_convert(linelist[1])
        # double quote any existing quotes in Payees then surround with quotes in case there is a comma
        linelist[2] = linelist[2].replace('"', '""')
        linelist[2] = '"' + linelist[2] + '"'
        # maketrans and translate changed from py2 to py3
        # this syntax only removes characters in 3rd param to maketrans
        linelist[4] = linelist[4].translate("".maketrans("", "", "$,"))
        # join with comma ..
        line = ",".join(linelist)
        print(line)
    else:
        # put line into corresponding places
        if line.strip() == "":
            # end of a section or a block
            if section_idx == num_columns - 1:
                # end of a block
                # write out the block
                serialize_block(block)
                # reinitialize
                block = []
                section_idx = 0
                row_idx = 0
            else:
                # end of a section
                section_idx += 1
                row_idx = 0
        else:
            if section_idx == 0:
                # first section of block
                # append empty row
                block.append([])
            # fix line contents in both 3 column checking and 5 column mastercard BMO statements
            if section_idx == 0 or (num_columns > 3 and section_idx == 1):
                # convert dates
                line = date_convert(line)
            elif (section_idx == 2 and num_columns > 3) or (
                section_idx == 1 and num_columns == 3
            ):
                # double quote any existing quotes in Payees then surround with quotes in case there is a comma
                line = line.replace('"', '""')
                # wrap with quotes
                line = '"' + line + '"'
            elif (section_idx == 4 and num_columns > 3) or (
                section_idx == 2 and num_columns == 3
            ):
                # remove unwanted characters
                line = line.translate("".maketrans("", "", "$,"))
                if line.strip().endswith("CR"):
                    # remove CR credit indicator
                    line.replace("CR", "")
                    # change sign, as credits are debits
                    line = "-" + line
            # add the line to the block row
            # ALT?: block[row_idx][section_idx] = line
            # print("BMO line %d %s" % (line_idx, line))
            block[row_idx].append(line)
            row_idx += 1
        # print("BMO line %d" % (line_idx))
    line_idx += 1
