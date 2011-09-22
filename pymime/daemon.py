#! /usr/bin/env python
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

import email
import logging
from pymime.config import mainconfig
import pymime.plugin
from multiprocessing.connection import Listener
from multiprocessing import Event, Process, cpu_count
from time import sleep
import signal


class ProcessManager(object):
    """
    This is the main object of pymimed. It runs and maintains the Worker processes.
    It is also responsible for setting up the logging and the socket Listener.
    """
    def __init__(self):
        self.logger = None
        self.setup_logging()
        self.logger.info("Listening on {0}:{1}".format(mainconfig.daemon.host, mainconfig.daemon.port))
        self.address = (mainconfig.daemon.host, int(mainconfig.daemon.port))
        self.listener = Listener(self.address, authkey = mainconfig.daemon.authkey)
        self.maxage = int(mainconfig.daemon.max_process_age)
        self.exit = False
        try:
            self.numprocess = cpu_count()
        except NotImplementedError:
            self.numprocess = 1
        self.processes = []

    def setup_logging(self):
        """
        Loads the logging configuration and sets up the root logger.
        """
        logging.basicConfig(level = mainconfig.logging.level,
                    format = '%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    filename = mainconfig.logging.file)
        self.logger = logging.getLogger()
        self.logger.info("="*72)
        try:
            if mainconfig.logging.maildest:
                from logging.handlers import SMTPHandler
                host = mainconfig.logging.smtp
                if mainconfig.logging.smtpport:
                    host = (host, mainconfig.logging.smtpport)
                    mailhandler = SMTPHandler(host,
                                  mainconfig.logging.mailfrom,
                                  mainconfig.logging.maildest.split(","),
                                  mainconfig.logging.mailsubject)
                    mailhandler.setLevel(mainconfig.logging.maillevel)
                    mailhandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)-12s %(message)s'))
                    self.logger.addHandler(mailhandler)
        except:
            self.logger.exception("Exception while trying to configure maillogging.")

    def start(self):
        signal.signal(signal.SIGHUP, self.reload)
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        self.logger.info("Setting up {0} Worker processes".format(self.numprocess))
        self.populate_processes()

    def join(self):
        while not self.exit:
            self.maintain_processes()
            sleep(0.1)

    def join_exited_processes(self):
        cleaned = False
        for i in reversed(range(len(self.processes))):
            process = self.processes[i]
            if process.exitcode is not None:
                process.join()
                if process.exitcode > 0:
                    self.logger.critical("Worker process aborted with exitcode {0}".format(process.exitcode))
                    self.logger.critical("If no other error was logged, this may be caused by an exception when loading the plugins.")
                    exit(1)
                cleaned = True
                del self.processes[i]
        return cleaned

    def populate_processes(self):
        for i in range(self.numprocess - len(self.processes)):
            p = Worker(self.listener, self.maxage)
            self.processes.append(p)
            p.daemon = True
            p.start()

    def maintain_processes(self):
        if self.join_exited_processes():
            self.populate_processes()

    def shutdown(self, signum = None, frame = None):
        self.logger.info("Initializing clean shutdown")
        self.exit = True
        for p in self.processes:
            p.shutdown()
        self.logger.info("Stopping to listen")
        self.listener.close()

    def reload(self, signum = None, frame = None):
        self.logger.info("===== Reloading configuration =====")
        for p in self.processes:
            p.shutdown()

class Worker(Process):
    """
    Waits for a job from a client and executes it.
    """
    def __init__(self, listener, maxage = None):
        self.listener = listener
        self.maxage = maxage
        self.completed = 0
        self.conn = None
        self.do_exit = Event()
        self.is_waiting = Event()
        self.logger = logging.getLogger("Worker")
        self.plugins = None
        super(Worker, self).__init__()
        self.logger.info("Initializing Worker")

    def run(self):
        self.logger = logging.getLogger("Worker{0}".format(self.pid))
        self.logger.info("Running Worker with PID {0}".format(self.pid))
        try:
            pymime.plugin.load_plugins()
        except:
            #Logging doesn't work here
            exit(1)
        self.plugins = pymime.plugin.PluginProvider.get_plugins() #@UndefinedVariable
        self.logger.info("Loaded Plugins: {0}".format(", ".join([plugin.name for plugin in self.plugins])))
        error = False
        while not self.do_exit.is_set() and (self.maxage is None or self.completed < self.maxage):
            self.is_waiting.set()
            # Don't ignore the Interrupt signal
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            self.logger.info("Waiting for job")
            self.conn = self.listener.accept()
            # Ignore the Interrupt signal unitl the connection is closed
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            self.is_waiting.clear()
            self.logger.info("Receiving data")
            try:
                data = self.conn.recv()
            except EOFError:
                self.logger.warning("Connection to client lost. Restarting worker.")
                self.conn.close()
                break
            message = email.message_from_string(data)
            for plugin in self.plugins:
                try:
                    message = plugin.parse(message)
                except:
                    error = True
                    self.logger.exception("An Error occured in plugin {0}".format(plugin.name))
            data = message.as_string()
            self.logger.info("Sending data")
            try:
                self.conn.send(data)
            except EOFError:
                self.logger.warning("Connection to client lost. Restarting worker.")
                self.conn.close()
                break
            self.conn.close()
            self.logger.info("Connection closed")
            self.completed += 1
            if error:
                self.logger.warning("An Error occured, restarting worker")
                break
        self.logger.info("Worker exits")

    def shutdown(self):
        self.logger.info("Shutting down worker")
        self.do_exit.set()
        self.terminate()
