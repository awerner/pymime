# -*- coding: utf-8 -*-

#    Copyright 2011 Christian Lohmaier, Alexander Werner
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

from pymime.plugin import PluginProvider
import pymime.plugins
import os.path
from pymime.utility import append_text
import email.utils
from string import Template

allowedlocals = {}
allowedlocals.update(dict((name, getattr(email.utils, name))for name in email.utils.__all__))

class Footer(PluginProvider):
    name = "Footer"
    order = 4
    hasconfig = True

    def __init__(self):
        super(Footer, self).__init__()
        self.defaultfile = self.config.footer.default
        self.defaultfile = self.parse_path(self.defaultfile)
        self.footer_map = {}
        self.template_map = {}
        self.build_footer_map()
        self.build_template_map()

    def parse_path(self, filename):
        if filename == "None":
            return None
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.abspath(pymime.globals.CONFIGDIR), filename)
            if not os.path.isfile(filename):
                filename = os.path.join(os.path.abspath(pymime.plugins.__path__[0]), filename)
        if not os.path.isfile(filename):
            raise IOError("File {0} does not exist.".format(filename))
        return filename

    def build_footer_map(self):
        for option in self.config.map:
            self.footer_map[option] = self.parse_path(self.config.footer[self.config.map[option]])

    def build_template_map(self):
        for option in self.config.template_identifiers:
            self.template_map[option] = self.config.template_identifiers[option]

    def generate_identifiers(self, message):
        identifiers = {}
        for identifier, value in message.items():
            identifiers[identifier] = value
        for identifier, code in self.template_map.items():
            headerlocal = [("header", dict(message.items())), ]
            try:
                identifiers[identifier] = eval(code, {"__builtins__":None}, dict(allowedlocals.items() + headerlocal))
            except:
                self.logger.exception("An exception occurred while parsing the template identifier {0}:".format(identifier))
        return identifiers

    def parse(self, message):
        filename = self.defaultfile
        if "To" in message:
            if message["To"] in self.footer_map:
                filename = self.footer_map[message["To"]]
        if not filename:
            return message
        try:
            with open(filename) as f:
                footer = f.read().decode("utf-8")
        except:
            self.logger.warning("Could not open or decode Footer {0}".format(filename))
        if footer:
            identifiers = self.generate_identifiers(message)
            template = Template(footer)
            footer = template.safe_substitute(identifiers)
            if not footer.startswith("\n"):
                footer = "\n" + footer
            append_text(message, footer)
        return message
