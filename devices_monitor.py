#!/usr/bin/env python
# -*- coding: utf-8-*-

import os
import time
import threading

import consts as C

from gi.repository import Gio
from gi.repository import GObject


class DevicesMonitor(GObject.GObject):

    __gsignals__ = {
        "connected": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
        "disconnected": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING])
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.monitors = {}
        self._handlers = {}
        self.deep_monitoring = False
        self.path = C.INPUT_PATH
        self.connecting_device = None

    def start(self):
        self._listen_to_directory(Gio.File.new_for_path(self.path))

    def _listen_to_directory(self, file):
        path = file.get_path()
        m = self.monitors[path] = file.monitor_directory(Gio.FileMonitorFlags.NONE, None)
        self._handlers[path] = m.connect("changed", self.__changed)

    def __changed(self, monitor, file, args, event):
        path = file.get_path()
        filename = os.path.basename(path)

        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            event, path = self.connecting_device
            self.connecting_device = None

            def send():
                time.sleep(0.1)  # It need to wait a little
                self.emit("connected", path)

            thread = threading.Thread(target=send)
            thread.start()

        elif event == Gio.FileMonitorEvent.DELETED:
            self.emit("disconnected", path)

        else:
            self.connecting_device = (event, path)
