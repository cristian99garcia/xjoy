#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import array
import struct
import threading

import utils as U
import consts as C
from devices_monitor import DevicesMonitor

from gi.repository import GLib
from gi.repository import GObject


class Joystick(GObject.GObject):

    __gsignals__ = {
        "button-pressed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
        "button-released": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
        "axis-moved": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING, GObject.TYPE_FLOAT]),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.file = None
        self.name = None
        self.axis_map = 0
        self.axis_states = {}
        self.button_map = 0
        self.button_states = {}

        self.connected = False
        self.watch_id = 0

    @classmethod
    def new_from_path(self, path):
        joy = Joystick()
        joy.set_from_file(path)

        return joy

    def set_from_file(self, file):
        self.file = file
        self.connected = True

        devfile = open(file, "rb")
        self.name = U.get_device_name(devfile)
        self.axis_map, self.axis_states = U.get_joystick_axis_map(devfile)
        self.button_map, self.button_states = U.get_joystick_button_map(devfile)

        self.watch_id = GObject.io_add_watch(devfile, GObject.IO_IN, self._watch_cb)

    def disconnect(self):
        self.connected = False
        GObject.source_remove(self.watch_id)
        self.watch_id = 0

    def _watch_cb(self, devfile, flag):
        evbuf = devfile.read(8)

        if evbuf:
            time, value, type, number = struct.unpack("IhBB", evbuf)

            #if type & 0x80:  # initial

            if type & 0x01:
                button = self.button_map[number]
                if button:
                    self.button_states[button] = value

                    if value:
                        self.emit("button-pressed", button)

                    else:
                        self.emit("button-released", button)

            if type & 0x02:
                axis = self.axis_map[number]
                if axis:
                    fvalue = value / 32767.0
                    self.axis_states[axis] = fvalue
                    self.emit("axis-moved", axis, fvalue)

        return True


class JoysticksManager(GObject.GObject):

    __gsignals__ = {
        "joysticks-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.joysticks = []

    def start(self):
        self.devices_monitor = DevicesMonitor()
        self.devices_monitor.connect("connected", self._connected)
        self.devices_monitor.connect("disconnected", self._disconnected)
        self.devices_monitor.start()

        self.check_for_joysticks()

    def disconnect_all(self):
        for joy in self.joysticks:
            joy.disconnect()

        del self.joysticks
        self.joysticks = []

    def check_for_joysticks(self):
        changed = False

        for name in os.listdir(C.INPUT_PATH):
            if name.startswith("js"):
                path = os.path.join(C.INPUT_PATH, name)

                joy = Joystick.new_from_path(path)
                self.joysticks.append(joy)

                changed = True

        if changed:
            self.emit("joysticks-changed")

    def _connected(self, monitor, path):
        if os.path.basename(path).startswith("js"):
            joy = Joystick.new_from_path(path)
            self.joysticks.append(joy)
            self.emit("joysticks-changed")

    def _disconnected(self, monitor, path):
        if os.path.basename(path).startswith("js"):
            joy = self.get_joystick_from_file(path)
            joy.disconnect()
            self.joysticks.remove(joy)
            self.emit("joysticks-changed")

    def get_joystick_from_file(self, file):
        for joy in self.joysticks:
            if joy.file == file:
                return joy

        return None

    def get_connected_joysticks(self):
        return self.joysticks
