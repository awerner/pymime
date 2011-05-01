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
import base64, hashlib, email.utils

class ArchiveHeader(PluginProvider):
    name="ArchiveHeader"
    order=1
    hasconfig=False

    def parse( self, message ):
        """
        Add mail-archive.com direct-link to archive http://www.mail-archive.com/faq.html#listserver
        """
        message_id = message['message-id']
        list_post = email.utils.parseaddr(message['to'])
        if ( message_id is not None ) and ( list_post[1] is not '' ):
            # remove < and > from msg-id
            sha = hashlib.sha1( message_id[1:-1] )
            sha.update( list_post[1] )
            hash = base64.urlsafe_b64encode( sha.digest() )
            url = "<http://go.mail-archive.com/%s>" % hash
            message['Archived-At'] = url
            # in case debugging is needed
            #message['X-Archived-At-msgid'] = message_id[1:-1]
            #message['X-Archived-At-list-post'] = list_post[1]
        return message
