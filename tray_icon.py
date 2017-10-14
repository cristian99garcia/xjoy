#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import GObject

import utils as U


class TrayIcon(Gtk.StatusIcon):

    __gsignals__ = {
        "show-hide-window": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self, items=[]):
        Gtk.StatusIcon.__init__(self)

        self.set_from_file(U.get_tray_icon_file())
        self.set_tooltip_text("XJoy")

        self.menu = Gtk.Menu()

        for label, callback in items:
            item = Gtk.MenuItem.new_with_mnemonic(label)

            if callback is not None:
                item.connect("activate", callback)

            self.menu.append(item)

        self.menu.show_all()

        self.connect("popup-menu", self._popup_menu)
        self.connect("activate", self._activate_cb)

    def _popup_menu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def _activate_cb(self, *args):
        self.emit("show-hide-window")
