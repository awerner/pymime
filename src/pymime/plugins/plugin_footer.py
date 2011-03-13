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

class Footer(PluginProvider):
    name="Footer"
    hasconfig=False

    def parse( self, message ):
        filename = None #TODO!
        rawfooter = None
        footer = None
        orig_cs = message.get_content_charset()
        if orig_cs == None:
            cs = "iso-8859-15"
            orig_cs = "ascii"
        else:
            cs = orig_cs
        try:
            with open( filename ) as f:
                rawfooter = f.read()
        except:
            pass
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
            del message["MIME-Version"]
            del message["Content-Transfer-Encoding"]
            message.set_payload( payload, cs )
        return message
