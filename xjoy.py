#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
import os
import sys
import signal

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject

import utils as U
import consts as C

from edit_area import EditArea
from joysticks_manager import JoysticksManager

USE_X = True  # TODO: detect wayland
if USE_X:
    sys.path.append("/home/cristian/Documentos/xjoy/xevents")

    from xevents.mouse import Mouse
    from xevents.keyboard import Keyboard


class XJoyWindow(Gtk.ApplicationWindow):

    __gsignals__ = {
        "finished-settings": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self, manager, setting, application=None):
        Gtk.ApplicationWindow.__init__(self, application=application)

        self.set_size_request(690, 428)
        self.set_resizable(False)
        self.set_title("XJoy")
        self.set_icon_from_file("data/icons/xjoy.svg")

        self.manager = manager

        self.edit_area = EditArea()
        self.edit_area.set_setting(setting)
        self.edit_area.connect("finished-settings", lambda e: self.emit("finished-settings"))
        self.add(self.edit_area)

        self.show_all()

    def set_setting(self, setting):
        self.edit_area.set_setting(setting)


class XJoyApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.zades.xjoy", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None

        self.mouse_direction = [0, 0]
        self.scroll_direction = [0, 0]
        self.mouse_movement_id = None
        self.scroll_id = None
        self.setting = False

        self.keyboard = Keyboard()
        self.mouse = Mouse()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        action = Gio.SimpleAction.new("open-settings", None);
        action.connect("activate", self.open_settings);
        self.set_accels_for_action("app.open-settings", ["<Primary>O"]);
        self.add_action(action);

        action = Gio.SimpleAction.new("save-settings", None);
        action.connect("activate", self.save_settings);
        self.set_accels_for_action("app.save-settings", ["<Primary>S"]);
        self.add_action(action);

        action = Gio.SimpleAction.new("reset-buttons", None);
        action.connect("activate", self.reset_buttons);
        self.set_accels_for_action("app.reset-buttons", ["<Primary>R"]);
        self.add_action(action);

    def do_activate(self):
        if not self.window:
            self.manager = JoysticksManager()
            self.manager.connect("joysticks-changed", self._joys_changed_cb)

            self.window = XJoyWindow(self.manager, self.setting, application=self)
            self.window.connect("delete-event", self._delete_event_cb)
            self.window.connect("finished-settings", self._set_cb)

            if C.TESTING:
                self.settings = C.TEST_SETTINGS
                self.window.edit_area.set_buttons(C.TEST_BUTTONS)

            else:
                self.settings = {}

            self.manager.start()  # FIXME: No debería estar acá, y si no va a haber ventana?

        self.window.present()

    def _delete_event_cb(self, *args):
        self.on_quit()

    def _joys_changed_cb(self, manager):
        joys = manager.get_connected_joysticks()

        joystick = joys[0]  # TODO: que el usuario elija
        joystick.connect("button-pressed", self._pressed_cb)
        joystick.connect("button-released", self._released_cb)
        joystick.connect("axis-moved", self._axis_moved_cb)

        self.window.edit_area.set_joystick(joystick)

    def _pressed_cb(self, joy, button):
        if self.setting:
            return

        if button in self.settings:
            self.emit_action(self.settings[button], C.ActionState.ON)

    def _released_cb(self, joy, button):
        if self.setting:
            return

        if button in self.settings:
            self.emit_action(self.settings[button], C.ActionState.OFF)

    def _axis_moved_cb(self, joy, axis, value):
        if self.setting:
            return

        if axis in self.settings:
            self.emit_action(self.settings[axis], value=U.abs(value))

    def emit_action(self, action, state=C.ActionState.OFF, value=0):
        if action.type == C.ActionType.MOUSE:
            subaction = action.data[0]
            if subaction == C.MouseActionType.MOVE_X:
                self.mouse_direction[0] = action.data[1] * value
                self.check_mouse_movement()

            elif subaction == C.MouseActionType.MOVE_Y:
                self.mouse_direction[1] = action.data[1] * value
                self.check_mouse_movement()

            elif subaction == C.MouseActionType.CLICK:
                if state == C.ActionState.ON:
                    self.mouse.press(button=action.data[1])

                elif state == C.ActionState.OFF:
                    self.mouse.release(button=action.data[1])

            elif subaction == C.MouseActionType.SCROLL_V:
                self.scroll_direction[0] = action.data[1] * U.invert_abs(value)
                self.check_scroll()

            elif subaction == C.MouseActionType.SCROLL_H:
                self.scroll_direction[1] = action.data[1] * value
                self.check_scroll()

        elif action.type == C.ActionType.KEYBOARD:
            for key in action.data:
                if state == C.ActionState.OFF:
                    self.keyboard.release_key(key)

                elif state == C.ActionState.ON:
                    self.keyboard.press_key(key)

    def _move_mouse(self):
        x, y = self.mouse.position()
        x += self.mouse_direction[0]
        y += self.mouse_direction[1]

        self.mouse.move(x, y)

        return True

    def _scroll(self):
        self.mouse.scroll(self.scroll_direction[0], self.scroll_direction[1])

        return True

    def check_mouse_movement(self):
        if self.mouse_direction == [0, 0] and self.mouse_movement_id is not None:
            GLib.source_remove(self.mouse_movement_id)
            self.mouse_movement_id = None

        elif self.mouse_direction != [0, 0] and self.mouse_movement_id is None:
            self.mouse_movement_id = GLib.timeout_add(50, self._move_mouse)

    def check_scroll(self):
        if self.scroll_direction == [0, 0] and self.scroll_id is not None:
            GLib.source_remove(self.scroll_id)
            self.scroll_id = None

        elif self.scroll_direction != [0, 0] and self.scroll_id is None:
            self.scroll_id = GLib.timeout_add(50, self._scroll)

    def open_settings(self, action, *args):
        dialog = Gtk.FileChooserDialog("Open a settings file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters_to_chooserdialog(dialog)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # TODO: Check for read permissions
            # TODO: Check if it's a real xjoy settings file
            self.settings, buttons = U.load_settings_from_file(dialog.get_filename())
            self.window.edit_area.set_buttons(buttons)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def save_settings(self, action, *args):
        dialog = Gtk.FileChooserDialog("Save settings", self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        self.add_filters_to_chooserdialog(dialog)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # TODO: Check for write permissions
            settings = U.convert_settings(self.settings, self.window.edit_area.get_buttons())
            U.save_settings(settings, dialog.get_filename())

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters_to_chooserdialog(self, dialog):
        data = [("XJoy Settings files", "*.xjs"), ("Any files", "*")]
        for name, pattern in data:
            filter_xjs = Gtk.FileFilter()
            filter_xjs.set_name(name)
            filter_xjs.add_pattern(pattern)
            dialog.add_filter(filter_xjs)

    def reset_buttons(self, action, *args):
        self.setting = True
        self.window.set_setting(True)

    def _set_cb(self, window):
        self.setting = False

    def on_quit(self, *args):
        self.manager.disconnect_all()
        self.quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = XJoyApp()
    sys.exit(app.run(sys.argv))
