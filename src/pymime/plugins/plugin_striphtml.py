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

import HTMLParser
from pymime.plugin import PluginProvider

#-------------------------------------------------------------------------------
# Configuration Options start here

IGNORETAGS = ( "script", "head", "title", "link" )
MAP_STARTTAGS = {"li": "\n* ",
                 "p": "\n"}
MAP_ENDTAGS = { "p": "\n",
               "div": "\n",
               "h1": "\n==============================================================\n\n",
               "h2": "\n--------------------------------------------------------------\n\n",
               "h3": "\n",
               "h4": "\n",
               "h5": "\n",
               "h6": "\n"}
MAXNUMNEWLINES = 2

# No Configuration beneath this line
# -------------------------------------------------------------------------------

class StripHTMLParser(HTMLParser.HTMLParser):
    """
    This class provides the necessary logic to convert HTML to plain text.
    """
    def __init__( self ):
        self.reset()
        self.plain = []
        self.last_starttag = None
    def handle_starttag( self, tag, attributes ):
        self.last_starttag = tag
        if tag in MAP_STARTTAGS:
            self.plain.append( MAP_STARTTAGS[tag] )
    def handle_endtag( self, tag ):
        if tag in MAP_ENDTAGS.keys():
            self.plain.append( MAP_ENDTAGS[tag] )
    def handle_data( self, data ):
        if self.last_starttag not in IGNORETAGS:
            self.plain.append( data.strip() )
    def remove_whitespace( self ):
        # Split at newlines instead of tags
        self.plain = "".join( self.plain ).split( "\n" )
        numspace = 0
        # Copy the whole text
        oldplain = self.plain[:]
        self.plain = []
        for line in oldplain:
            if line.isspace() or line is "":
                numspace = numspace + 1
                if numspace <= MAXNUMNEWLINES:
                    # number of blank newlines is lower than limit, append line
                    self.plain.append( "\n" )
            else:
                numspace = 0
                # line is no blank newline, append line
                self.plain.append( line )
    def get_plain_data( self ):
        self.remove_whitespace()
        return "\n".join( self.plain )


class StripHTML(PluginProvider):
    name="StripHTML"
    hasconfig=False

    def __init__(self):
        super(StripHTML,self).__init__()
        self.message=None

    def parse(self,message):
        self.message=message
        if self.message.is_multipart():
            self.parse_multipart()
        else:
            self.parse_singlepart()
        return self.message

    def parse_singlepart( self, message=None ):
        """
        Parses a singlepart message object.
        """
        param=True
        if not message:
            param=False
            message = self.message
        content_type = message.get_content_type()
        if content_type == "text/html":
            # text/html must be stripped down to text/plain
            s = StripHTML()
            # Feed the HTML-Stripper with the body of the message
            s.feed( message.get_payload() )
            # And set the body of the message to the output of the HTML-Stripper 
            message.set_payload( s.get_plain_data() )
            # rewrite the Content-Type header, im no longer an evil HTML mail :)
            message.set_type( "text/plain" )
        if param:
            return message
        else:
            self.message=message

    def parse_multipart( self ):
        """
        Parses a multipart message object.
        """
        mails = []
        #---------------------------------------------------------------------------
        # Test if the message has a text/plain and a text/html part
        has_plaintext = False
        has_html = False
        for part in self.message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                has_plaintext = True
            if content_type == "text/html":
                has_html = True
        #---------------------------------------------------------------------------
        # If the message has both text/plain and text/html parts, dismiss the text/html part.
        if has_plaintext and has_html:
            for part in self.message.walk():
                content_type = part.get_content_type()
                if content_type != "text/html":
                    if not part.is_multipart():
                        mails.append( part )
        elif not has_plaintext and has_html:
            for part in self.message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    part = self.parse_singlepart(part)
                if not part.is_multipart():
                    mails.append(part)
        else:
            for part in self.message.walk():
                if not part.is_multipart():
                    mails.append( part )
        #---------------------------------------------------------------------------
        # Test if at least one submessage survived the parsing
        if mails:
            # Delete the body from the message
            self.message.set_payload( None )
            # Only one submessage to be included in the body, a restructuring of the parent
            # message is necessary.
            if len( mails ) == 1:
                mail = mails[0]
                # Copy the Headers from the submessage to the parent message
                for key in mail.keys():
                    del self.message[key]
                    self.message[ key] = mail[key]
                # If the parent message is still multipart, the submessage didn't have a Content-Type
                # Header. Replace the old parent Content-Type with a default.
                if "multipart" in self.message.get_content_maintype():
                    del self.message["Content-Type"]
                    self.message["Content-Type"] = "text/plain"
                # Copy the body from the submessage to teh parent message
                self.message.set_payload( mails[0].get_payload() )
            # Multiple submessages are to be included, simply attach them.
            else:
                for mail in mails:
                    self.message.attach( mail )
        # No Message is to be included
        else:
            raise Exception
