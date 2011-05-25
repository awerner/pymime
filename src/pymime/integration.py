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
import sys

def dummy_store(attachments, headers, options, policy_options):
    """
    Simple store-function that returns a text with the number of attachments
    and does nothing with them, so they are lost.
    """
    return "Number of Attachments: {0}".format(len(attachments))

def flat_store(attachments, headers, options, policy_options):
    """
    This store-function saves the detached attachments in the directory options["path"]
    (default: current working dir + store).
    Subdirectories containing the attachments are created named after the sha1-hash of the attachment, salted with options["salt"].
    If specified, options["text_after"] is appended to the attachment list.
    """
    salt = ""
    if options and "salt" in options:
        salt = options["salt"]
    path = os.path.join(os.getcwd(), "store")
    if options and "path" in options:
        path = options["path"]
    baseurl = "http://localhost/"
    if options and "baseurl" in options:
        baseurl = options["baseurl"]
    text_after = ""
    if options and "text_after" in options:
        text_after = options["text_after"]
    footer = "Number of allowed Attachments: {0}".format(len(attachments))
    for part in attachments:
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                ext = '.bin'
            filename = "{0}{1}".format("attachment", ext)
        h = hashlib.sha1(salt) #@UndefinedVariable
        h.update(part.get_payload(decode = True))
        hex = h.hexdigest()
        dir = os.path.join(path, hex)
        filepath = os.path.join(dir, filename)
        try:
            os.makedirs(dir)
        except os.error:
            pass
        fp = open(filepath, 'wb')
        fp.write(part.get_payload(decode = True))
        fp.close()
        fullurl = "{0}{1}/{2}".format(baseurl, hex, filename)
        footer += "\nAttachment: {0}".format(fullurl)
    footer += text_after
    return footer

def django_store(attachments, headers, options, policy_options):
    if options and not "project-path" in options and not "settings-module" in options:
        raise AttributeError("Not properly configured.")
    baseurl = "http://localhost/"
    if "baseurl" in options:
        baseurl = options["baseurl"]
    if "project-path" in options:
        sys.path.append(options["project-path"])
    if "settings-module" in options:
        modname, sep, setname = options["settings-module"].rpartition(".") #@UnusedVariable
        mod = __import__(modname, fromlist = [setname])
        settings = getattr(mod, setname)
    else:
        import settings #@UnresolvedImport
    from django.core.management import setup_environ
    setup_environ(settings)
    from pymime.django_app.pymime_attachmentservice.models import Mail, Attachment
    from django.core.files.base import ContentFile
    m = Mail()
    m.subject = headers["Subject"]
    m.sender = headers["From"]
    m.receiver = headers["To"]
    if policy_options and "max-age" in policy_options:
        m.max_age = int(policy_options["max-age"])
    if "Archived-At" in headers:
        m.archive_url = headers["Archived-At"].strip("<>")
    m.save()
    for part in attachments:
        a = Attachment()
        a.mail = m
        a.content_type = part.get_content_type()
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(a.content_type)
            if not ext:
                ext = '.bin'
            filename = "{0}{1}".format("attachment", ext)
        a.filename_orig = filename
        a.file.save(a.filename_orig, ContentFile(part.get_payload(decode = True)), save = True)
        a.save()
    url = "{0}{1}".format(baseurl.rstrip("/"), m.get_absolute_url())
    return "Attachments are available at {0}".format(url)
