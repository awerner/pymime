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

import logging
from pymime.config import ConfigWrapper
import pymime.plugins
import pkgutil

class PluginRoot(type):
    """
    Metaclass of all plugins.
    At plugin class definition, the class is added to the plugins list of the plugin provider.
    """
    def __init__(cls, *args, **kwargs):
        if not hasattr(cls, 'plugins'):
            cls.plugins=[]
        else:
            cls.plugins.append(cls)

    def get_plugins(cls, *args, **kwargs):
        """
        Return a list of instances of all registered plugins. Options can be passed to the constructors as parameters of this method.
        """
        return [p(*args,**kwargs) for p in cls.plugins]


class PluginProvider(object):
    """
    Parent of all Plugins.
    """
    __metaclass__=PluginRoot
    name="Metaplugin"
    """Name of the plugin. Must be overwritten."""
    hasconfig=False
    """
    True if the plugin has its own configuration file.
    The file will be loaded at instantiation and searched for in pymime.globals.CONFIGDIR and in the plugins directory with the name plugin_NAME.conf and plugin_NAME.conf.default repectively.
    """
    config=None
    """
    An Instance of the pymime.config.ConfigWrapper for easy access to configuration values if the plugin has an own configuration file.
    """
    def __init__(self):
        self.logger=logging.getLogger(self.name)
        if self.hasconfig:
            self.config = ConfigWrapper(self.name)
    def parse(self, message):
        self.logger.warning("method parse not implemented")
        return message


def load_plugins():
    package=pymime.plugins
    for importer, name, ispkg in pkgutil.walk_packages(
        path=package.__path__,
        prefix=package.__name__+".",
        onerror=lambda x: None):
        __import__(name)
