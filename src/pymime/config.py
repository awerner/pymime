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

import pymime.globals
import pymime.plugins
from ConfigParser import SafeConfigParser
import os

class ConfigWrapper(object):
    def __init__(self, plugin_namespace=None):
        self.config=SafeConfigParser()
        if plugin_namespace:
            filename="plugin_"+plugin_namespace+".conf"
        else:
            filename="pymime.conf"
        self.path=os.path.join(pymime.globals.CONFIGDIR,filename)
        if not os.path.isfile(self.path):
            if plugin_namespace:
                self.path=os.path.join(os.path.abspath(pymime.plugins.__path__[0]),"plugin_"+plugin_namespace+".conf")
            else:
                self.path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"pymime.conf.default")
            if not os.path.isfile(self.path):
                raise IOError("No Configuration found")
        self.config.read(self.path)
    def __getattr__(self,name):
        if self.config.has_section(name):
            return SectionWrapper(self.config, name)
        else:
            raise AttributeError("No Section {0} in File {1}".format(name,self.path))

class SectionWrapper(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section
    def __getattr__(self,name):
        if self.config.has_option(self.section,name):
            return self.config.get(self.section,name)
        else:
            raise AttributeError

mainconfig = ConfigWrapper()
