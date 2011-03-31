# -*- coding: utf-8 -*-

#    Copyright 2011 Christian Lohmeier, Alexander Werner
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

class Footer(PluginProvider):
    name="Footer"
    hasconfig=True

    def __init__(self):
        super(Footer,self).__init__()
        self.defaultfile=self.config.footer.default
        if self.defaultfile == "None":
            self.defaultfile=None
        elif not os.path.isabs(self.defaultfile):
            self.defaultfile=self.prepend_plugin_path(self.defaultfile)

    def prepend_plugin_path(self,filename):
        return os.path.join(os.path.abspath(pymime.plugins.__path__[0]),filename)

    def parse( self, message, walk=True, rawfooter=None ):
        # Load footerfile before walking through the parts
        # And pass the rawfooter to the parts
        if walk and message.is_multipart():
            for part in message.walk():
                if part.get_content_type().startswith("text/"):
                    self.parse(part)
        filename = self.defaultfile
        footer = None
        orig_cs = message.get_content_charset()
        if orig_cs == None:
            cs = "iso-8859-15"
            orig_cs = "ascii"
        else:
            cs = orig_cs
        if not rawfooter:
            try:
                with open( filename ) as f:
                    rawfooter = f.read()
            except:
                self.logger.warning("Could not open Footer {0}".format(filename))
        if rawfooter:
            try:
                footer = rawfooter.decode( "utf-8" ).encode( cs )
            except:
                cs = "utf-8"
                footer = rawfooter.decode( "utf-8" ).encode( cs )
        if footer:
            sep = "\n"
            if footer.startswith( "\n" ):
                sep = ""
            payload = message.get_payload( decode = True ).decode( orig_cs ).encode( cs ) + sep + footer
            try:
                del message["MIME-Version"]
            except:
                pass
            try:
                del message["Content-Transfer-Encoding"]
            except:
                pass
            message.set_payload( payload, cs )
        return message
