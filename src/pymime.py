#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script takes a MIME-formatted email and does various transformations with it,
e.g. converts HTML-mails to plain text mails and strips attachements.
"""
import HTMLParser, email, sys

IGNORETAGS = ( "script", "head", "title", "link" )
MAP_STARTTAGS = {"li": "\n* "}
MAP_ENDTAGS = { "p": "\n", "div": "\n"}
MAXNUMNEWLINES = 2

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
    def get_string( self ):
        return self.message.as_string()


if __name__ == "__main__":
    e = EMail()
    #e.feed( fp = sys.stdin  )
    e.feed( fp = file( "test.eml" ) )
    e.parse()
    print e.get_string()
