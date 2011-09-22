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
import subprocess
import logging


class Client(object):
    def __init__(self):
        self.logger = None
        self.setup_logging()
        self.input = None
        self.output = None
        self.parse_opts()

    def run(self):
        self.start_daemon()
        self.send()

    def parse_opts(self):
        parser = OptionParser()
        parser.add_option("-i", "--input", dest = "input", default = "-",
                           help = "Where to read the mail from. Defaults to STDIN")
        parser.add_option("-o", "--output", dest = "output", default = "-",
                           help = "Where to write the transformed mail. Defaults to STDOUT")
        options, args = parser.parse_args()

        if options.input == "-":
            self.input = sys.stdin
        else:
            self.input = file(options.input)

        if options.output == "-":
            self.output = sys.stdout
        else:
            self.output = file(options.output, "w")

    def setup_logging(self):
        self.logger = logging.getLogger()
        self.logger.addHandler(logging.NullHandler())
        if mainconfig.logging.maildest:
            from logging.handlers import SMTPHandler
            host = mainconfig.logging.smtp
            if mainconfig.logging.smtpport:
                host = (host, mainconfig.logging.smtpport)
                mailhandler = SMTPHandler(host,
                              mainconfig.logging.mailfrom,
                              mainconfig.logging.maildest.split(","),
                              mainconfig.logging.mailsubject)
                mailhandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)-12s %(message)s'))
                self.logger.setLevel(mainconfig.logging.maillevel)
                self.logger.addHandler(mailhandler)

    def start_daemon(self):
        try:
            if mainconfig.client.start_daemon:
                try:
                    pf = file(mainconfig.daemon.pidfile, 'r')
                    pid = int(pf.read().strip())
                    pf.close()
                except (IOError, ValueError):
                    pid = None
                if not pid:
                    subprocess.Popen(["pymimed", "start"])
                    self.logger.warning("Pymimed seems not to be running. Trying to start it.")
        except:
            self.logger.exception("Exception occured while trying to start pymimed from pymimec.")

    def send(self):
        try:
            address = (mainconfig.client.host, int(mainconfig.client.port))
            conn = multiprocessing.connection.Client(address, authkey = mainconfig.client.authkey)
            conn.send(self.input.read())
            self.input.close()
            self.output.write(conn.recv())
            conn.close()
            self.output.close()
        except:
            self.logger.exception("Exception occured in pymimec")
