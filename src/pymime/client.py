#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2011 Alexander Werner
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing.connection
from optparse import OptionParser
from pymime.config import mainconfig
import sys

parser = OptionParser()
parser.add_option("-i", "--input", dest = "input", default = "-",
                   help = "Where to read the mail from. Defaults to STDIN")
parser.add_option("-o", "--output", dest = "output", default = "-",
                   help = "Where to write the transformed mail. Defaults to STDOUT")
options, args = parser.parse_args()

if options.input == "-":
    input = sys.stdin
else:
    input = file(options.input)

if options.output == "-":
    output = sys.stdout
else:
    output = file(options.output, "w")

address = (mainconfig.client.host, int(mainconfig.client.port))
conn = multiprocessing.connection.Client(address, authkey = mainconfig.client.authkey)

conn.send(input.read())
input.close()
output.write(conn.recv())
conn.close()
output.close()
