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
from StringIO import StringIO
from email.generator import Generator
from email.utils import parseaddr
import os
import ast
from pymime.utility import append_text, unicode_header
import logging

class AttachmentPolicy(object):
    def __init__(self, configsection, fallback = None):
        self.name = configsection.section
        self.logger = logging.getLogger("AttachmentPolicy({0})".format(self.name))
        self.policy = self._call_with_fallback(self._parse_policy, configsection, "policy", fallback)
        self.action = self._call_with_fallback(self._parse_action, configsection, "action", fallback)
        self.max_size = self._call_with_fallback(self._parse_max_size, configsection, "max_size", fallback)
        self.mime = self._call_with_fallback(self._parse_list, configsection, "mime", fallback)
        self.ext = self._call_with_fallback(self._parse_list, configsection, "ext", fallback)
        self.store_function_options = self._call_with_fallback(self._parse_store_function_option, configsection, "store-function-options", fallback)

    def _call_with_fallback(self, func, dictionary, key, fallback = None):
        try:
            return func(dictionary[key])
        except:
            if fallback:
                return func(fallback[key])
            else:
                raise

    def _parse_policy(self, value):
        value = value.lower()
        if value in ["whitelist", "blacklist"]:
            return value
        else:
            raise ValueError("Unrecognized policy: {0}".format(value))

    def _parse_action(self, value):
        value = value.lower()
        if value in ["keep", "store"]:
            return value
        else:
            raise ValueError("Unrecognized action: {0}".format(value))

    def _parse_max_size(self, value):
        if value.isdigit():
            return int(value)
        elif value[:-1].isdigit():
            if value[-1:].lower() in ["k", "m", "g"]:
                map = {"k":1024, "m":1024 ** 2, "g":1024 ** 3}
                value = int(value[:-1]) * map[value[-1:].lower()]
                return value
            else:
                raise ValueError("Unrecognized file size: {0}".format(value))
        else:
            raise ValueError("Unrecognized file size: {0}".format(value))

    def _parse_list(self, value):#
        value = value.split(",")
        value = map(lambda s: s.strip(), value)
        return value

    def _parse_store_function_option(self, value):
        try:
            return ast.literal_eval(value)
        except:
            self.logger.warning("store-function-options invalid")
            return None

    def check_mime_allowed(self, message):
        content_type = message.get_content_type()
        for mime in self.mime:
            if content_type.startswith(mime):
                status = (self.policy == "whitelist")
                break
            else:
                status = (self.policy != "whitelist")
        text = ""
        if not status:
            text = "NOT"
        self.logger.info("MIME type of {0}({1}) is {2} allowed".format(message.get_filename(), content_type, text))
        return status

    def check_ext_allowed(self, message):
        filename = message.get_filename()
        if filename:
            for ext in self.ext:
                if filename.lower().endswith(ext.lower()):
                    status = (self.policy == "whitelist")
                    break
                else:
                    status = (self.policy != "whitelist")
        else:
            status = False
        text = ""
        if not status:
            text = "NOT"
        self.logger.info("Extension of {0} is {1} allowed".format(filename, text))
        return status

    def check_size_allowed(self, message):
        fp = StringIO()
        g = Generator(fp)
        g.flatten(message)
        fp.seek(0, os.SEEK_END)
        fpsize = fp.tell()
        status = (fpsize <= self.max_size)
        if not status:
            self.logger.info("Size of message is {0}, but only {1} is allowed.".format(fpsize, self.max_size))
        return status

class AttachmentService(PluginProvider):
    name = "AttachmentService"
    order = 3
    hasconfig = True

    def __init__(self):
        super(AttachmentService, self).__init__()
        self.defaultpolicy = AttachmentPolicy(self.config["policy-default"])
        self.store_function = self._get_store_function()
        self.store_function_options = self._get_store_function_options()
        self.policy_map = {}
        self.build_policy_map()

    def _get_store_function(self):
        try:
            funcname = self.config["default"]["store-function"]
            modname, sep, funcname = funcname.rpartition(".")
            mod = __import__(modname, fromlist = [funcname])
            return getattr(mod, funcname)
        except:
            self.logger.exception("store-function is invalid")
            return False

    def _get_store_function_options(self):
        try:
            return ast.literal_eval(self.config["default"]["store-function-options"])
        except:
            self.logger.warning("store-function-options invalid")
            return None

    def build_policy_map(self):
        for option in self.config.map:
            self.policy_map[option] = AttachmentPolicy(self.config["policy-" + self.config.map[option]], self.config["policy-default"])

    def check_size(self, message, policy):
        if policy.check_size_allowed(message):
            return True
        else:
            self.logger.info("Dropping all attachments because mail is to large.")
            payload = []
            dropped = []
            for part in message.get_payload():
                if part.get_content_maintype() == "text":
                    payload.append(part)
                else:
                    dropped.append(part.get_filename())
            message.set_payload(None)
            for part in payload:
                message.attach(part)
            append_text(message, "\n--\nAttachments were dropped because the size of the mail was too large:\n" + "\n".join(dropped))
            return False

    def parse(self, message):
        policy = self.defaultpolicy
        dropped_attachments = []
        if "To" in message:
            addr = parseaddr(message["To"])[1]
            if addr in self.policy_map:
                policy = self.policy_map[addr]
                self.logger.info("Policy for {0} found: {1}".format(addr, policy.name))
        if not policy:
            self.logger.warning("No default policy! Returning Message unaltered.")
            return message
        if message.is_multipart():
            if not self.check_size(message, policy):
                return message
            payload = []
            for part in message.walk():
                dropped = None
                ct = part.get_content_type()
                if ct.startswith("multipart/"):
                    continue
                if not ct.startswith("text/"):
                    part, dropped = self.parse_part(part, policy)
                if part is not None:
                    payload.append(part)
                if dropped is not None:
                    dropped_attachments.append(dropped)
            if policy.action == "keep":
                message.set_payload(None)
                for part in payload:
                    message.attach(part)
                if dropped_attachments:
                    append_text(message, "\n--\nThese attachments were dropped because their MIME-type or extension is not allowed:\n" +
                                "\n".join([dropped.get_filename() or "" for dropped in dropped_attachments]))
            elif policy.action == "store":
                message.set_payload(None)
                attachments = []
                for part in payload:
                    ct = part.get_content_type()
                    if ct.startswith("text/"):
                        message.attach(part)
                    else:
                        attachments.append(part)
                headers = dict()
                for name, content in message.items():
                    headers[name] = unicode_header(content)
                append_text(message, "\n--\n" + self.store_function(attachments, dropped_attachments, headers, self.store_function_options, policy.store_function_options))
        return message

    def parse_part(self, message, policy):
        if not(policy.check_mime_allowed(message) and
               policy.check_ext_allowed(message)):
            return None, message
        return message, None
