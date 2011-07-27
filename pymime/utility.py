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

import email.header

def append_text(message, text):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type().startswith("text/"):
                append_text(part, text)
        return
    orig_cs = message.get_content_charset()
    if orig_cs == None:
        cs = "iso-8859-15"
        orig_cs = "ascii"
    else:
        cs = orig_cs
    try:
        text = text.encode(cs)
    except:
        cs = "utf-8"
        text = text
    payload = message.get_payload(decode = True).decode(orig_cs).encode(cs) + text
    try:
        del message["MIME-Version"]
    except:
        pass
    try:
        del message["Content-Transfer-Encoding"]
    except:
        pass
    message.set_payload(payload, cs)

def unicode_header(header):
    parts = email.header.decode_header(header)
    decoded_list=[]
    for part in parts:
        part_string, part_encoding = part
        if part_encoding:
            decoded_list.append(part_string.decode(part_encoding))
        else:
            decoded_list.append(part_string)
    return u" ".join(decoded_list)
