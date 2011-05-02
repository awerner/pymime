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

import mimetypes
import hashlib
import os

def dummy_store(attachments, options):
    """
    Simple store-function that returns a text with the number of attachments
    and does nothing with them, so they are lost.
    """
    return "Number of Attachments: {0}".format(len(attachments))

def flat_store(attachments,options):
    """
    This store-function saves the detached attachments in the directory options["path"]
    (default: current working dir + store).
    Subdirectories containing the attachments are created named after the sha1-hash of the attachment, salted with options["salt"].
    If specified, options["text_after"] is appended to the attachment list.
    """
    salt = ""
    if hasattr(options,"salt"):
        salt = options["salt"]
    path = os.path.join(os.getcwd(),"store")
    if hasattr(options,"path"):
        path=options["path"]
    baseurl="http://localhost/"
    if hasattr(options,"baseurl"):
        baseurl=options["baseurl"]
    text_after=""
    if hasattr(options, "text_after"):
        text_after=options["text_after"]
    footer="Number of allowed Attachments: {0}".format(len(attachments))
    for part in attachments:
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                ext = '.bin'
            filename = "{0}{1}".format("attachment",ext)
        h = hashlib.sha1(salt) #@UndefinedVariable
        h.update(part.get_payload(decode=True))
        hex = h.hexdigest()
        dir = os.path.join(path,hex)
        filepath=os.path.join(dir,filename)
        try:
            os.makedirs(dir)
        except os.error:
            pass
        fp = open(filepath, 'wb')
        fp.write(part.get_payload(decode=True))
        fp.close()
        fullurl="{0}{1}/{2}".format(baseurl,hex,filename)
        footer+="\nAttachment: {0}".format(fullurl)
    footer+=text_after
    return footer
