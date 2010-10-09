#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script takes a MIME-formatted email and does various transformations with it,
e.g. converts HTML-mails to plain text mails and strips attachements.
"""
import HTMLParser

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

if __name__ == "__main__":
    s = StripHTML()
    with file( "test.html" ) as f:
        s.feed( f.read() )
    with file( "test", "w" ) as f:
        f.write( s.get_plain_data() )
