#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script takes a MIME-formatted email and does various transformations with it,
e.g. converts HTML-mails to plain text mails and strips attachements.
"""
import HTMLParser, email, sys
from optparse import OptionParser

IGNORETAGS = ( "script", "head", "title", "link" )
MAP_STARTTAGS = {"li": "\n* "}
MAP_ENDTAGS = { "p": "\n", "div": "\n"}
MAXNUMNEWLINES = 2


parser = OptionParser()
parser.add_option( "-i", "--input", dest = "input", default = "-",
                   help = "Where to read the mail from. Defaults to STDIN" )
parser.add_option( "-o", "--output", dest = "output", default = "-",
                   help = "Where to write the transformed mail. Defaults to STDOUT" )
options, args = parser.parse_args()


class StripHTML( HTMLParser.HTMLParser ):
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
        self.plain = " ".join( self.plain ).split( "\n" )
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

class EMail( object ):
    def __init__( self ):
        self.to_include = False
    def feed( self, fp = None, string = None, message = None ):
        if fp is not None:
            self.message = email.message_from_file( fp )
        elif string is not None:
            self.message = email.message_from_string( string )
        elif message is not None:
            self.message = message
        else:
            raise AttributeError
    def parse( self ):
        if self.message.is_multipart():
            self.parse_multipart()
        else:
            self.parse_singlepart()
    def parse_multipart( self ):
        mails = []
        has_plaintext = False
        has_html = False
        for part in self.message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                has_plaintext = True
            if content_type == "text/html":
                has_html = True
        if has_plaintext and has_html:
            for part in self.message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    mails.append( part )
        else:
            for part in self.message.walk():
                content_type = part.get_content_type()
                if content_type in ["multipart/alternative", "multipart/related"]:
                    continue
                mail = EMail()
                mail.feed( message = part )
                mail.parse()
                if mail.to_include:
                    mails.append( mail.message )
        if mails:
            self.message.set_payload( None )
            if len( mails ) == 1:
                del self.message["Content-Type"]
                self.message["Content-Type"] = mails[0]["Content-Type"]
                self.message.set_payload( mails[0].get_payload() )
            else:
                for mail in mails:
                    self.message.attach( mail )
        else:
            raise Exception
    def parse_singlepart( self ):
        content_type = self.message.get_content_type()
        if content_type == "text/plain":
            self.to_include = True
        elif content_type == "text/html":
            s = StripHTML()
            s.feed( self.message.get_payload() )
            self.message.set_payload( s.get_plain_data() )
            self.to_include = True
            for key in self.message.keys():
                del self.message[key]
    def get_string( self ):
        return self.message.as_string()


if __name__ == "__main__":
    if options.input == "-":
        input = sys.stdin
    else:
        input = file( options.input )
    if options.output == "-":
        output = sys.stdout
    else:
        output = file( options.output, "w" )
    e = EMail()
    e.feed( fp = input )
    e.parse()
    output.write( e.get_string() )
    output.close()
