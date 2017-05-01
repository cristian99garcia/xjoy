#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
import os

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GObject

from joysticks_manager import JoysticksManager
from edit_area import EditArea


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_size_request(690, 428)
        self.set_resizable(False)
        self.set_title("XJoy")
        self.connect("delete-event", self._exit)

        self.manager = JoysticksManager()
        self.manager.connect("joysticks-changed", self._joys_changed_cb)

        self.edit_area = EditArea()
        self.add(self.edit_area)

        self.manager.start()
        self.show_all()

    def _joys_changed_cb(self, manager):
        joys = manager.get_connected_joysticks()
        self.edit_area.set_joystick(joys[0])

    def _exit(self, window, event):
        self.manager.disconnect_all()
        Gtk.main_quit()

        return False


if __name__ == "__main__":
    MainWindow()
    Gtk.main()
