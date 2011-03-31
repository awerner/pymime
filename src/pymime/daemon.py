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
import pymime.globals
from pymime.config import mainconfig
import pymime.plugin
from multiprocessing.connection import Listener
from multiprocessing import Event, Process, cpu_count
from time import sleep
import signal
import sys


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    filename=mainconfig.daemon.logfile)
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.info(72*"=")
ROOT_LOGGER.info("Startup")


class ProcessManager(object):
    """
    Runs the Worker processes that listen at the address.
    """
    address = (mainconfig.daemon.host, int(mainconfig.daemon.port))
    listener = Listener(address, authkey=mainconfig.daemon.authkey)
    maxage = int(mainconfig.daemon.max_process_age)
    try:
        numprocess = cpu_count()
    except NotImplementedError:
        numprocess = 1

    def __init__(self):
        ROOT_LOGGER.info("Listening on {0}:{1}".format(mainconfig.daemon.host,mainconfig.daemon.port))
        self.processes=[]

    def start(self):
        ROOT_LOGGER.info("Setting up {0} Worker processes".format(self.numprocess))
        self.populate_processes()

    def join(self):
        try:
            while True:
                self.maintain_processes()
                sleep(0.1)
        except KeyboardInterrupt:
            ROOT_LOGGER.info("Initializing clean shutdown")
            self.shutdown()

    def join_exited_processes(self):
        cleaned = False
        for i in reversed(range(len(self.processes))):
            process = self.processes[i]
            if process.exitcode is not None:
                process.join()
                if process.exitcode>0:
                    ROOT_LOGGER.critical("Worker process aborted with exitcode {0}".format(process.exitcode))
                    ROOT_LOGGER.critical("If no other error was logged, this may be caused by an exception when loading the plugins.")
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

    def shutdown(self):
        for p in self.processes:
            p.shutdown()
        ROOT_LOGGER.info("Stopping to listen")
        self.listener.close()


class Worker(Process):
    """
    Waits for a job from a client and executes it.
    """
    def __init__(self, listener, maxage=None):
        self.listener = listener
        self.maxage = maxage
        self.completed = 0
        self.conn = None
        self.do_exit = Event()
        self.is_waiting = Event()
        self.logger = logging.getLogger("Worker")
        self.plugins = None
        super(Worker,self).__init__()
        self.logger.info("Initializing Worker")

    def run(self):
        self.logger = logging.getLogger("Worker{0}".format(self.pid))
        self.logger.info("Running Worker with PID {0}".format(self.pid))
        try:
            pymime.plugin.load_plugins()
        except:
            #Logging doesn't work here
            exit(1)
        self.plugins=pymime.plugin.PluginProvider.get_plugins()
        self.logger.info("Loaded Plugins: {0}".format(", ".join([plugin.name for plugin in self.plugins])))
        error=False
        while not self.do_exit.is_set() and (self.maxage is None or self.completed < self.maxage):
            self.is_waiting.set()
            # Don't ignore the Interrupt signal
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            self.logger.info("Waiting for job")
            self.conn = self.listener.accept()
            # Ignore the Interrupt signal unitl the connection is closed
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.is_waiting.clear()
            self.logger.info("Receiving data")
            data=self.conn.recv()
            message=email.message_from_string(data)
            for plugin in self.plugins:
                try:
                    message=plugin.parse(message)
                except:
                    error=True
                    self.logger.exception("An Error occured in plugin {0}".format(plugin.name))
            data=message.as_string()
            self.logger.info("Sending data")
            self.conn.send(data)
            self.conn.close()
            self.logger.info("Connection closed")
            self.completed+=1
            if error:
                self.logger.warning("An Error occured, restarting worker")
                break
        self.logger.info("Worker exits")

    def shutdown(self):
        self.logger.info("Shutting down worker")
        self.do_exit.set()


if __name__=="__main__":
    p = ProcessManager()
    p.start()
    p.join()
