#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
import os
import sys

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

import utils as U
import consts as C

from edit_area import EditArea
from joysticks_manager import JoysticksManager

USE_X = True  # TODO: detect wayland
if USE_X:
    sys.path.append("/home/cristian/Documentos/xjoy/xevents")

    from xevents.mouse import Mouse
    from xevents.keyboard import Keyboard


TESTING = True


class XJoyWindow(Gtk.ApplicationWindow):

    def __init__(self, manager, application=None):
        Gtk.ApplicationWindow.__init__(self, application=application)

        self.set_size_request(690, 428)
        self.set_resizable(False)
        self.set_title("XJoy")

        self.manager = manager

        self.edit_area = EditArea()
        self.add(self.edit_area)

        self.show_all()


class XJoyApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.zades.xjoy", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None

        self.mouse_direction = [0, 0]
        self.scroll_direction = [0, 0]
        self.mouse_movement_id = None
        self.scroll_id = None

        self.keyboard = Keyboard()
        self.mouse = Mouse()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        if not self.window:
            self.manager = JoysticksManager()
            self.manager.connect("joysticks-changed", self._joys_changed_cb)

            self.window = XJoyWindow(self.manager, application=self)
            self.window.connect("delete-event", self._delete_event_cb)

            if TESTING:
                self.settings = C.TEST_SETTINGS

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
        if button in self.settings:
            self.emit_action(C.TEST_SETTINGS[button], C.ActionState.ON)

    def _released_cb(self, joy, button):
        if button in self.settings:
            self.emit_action(C.TEST_SETTINGS[button], C.ActionState.OFF)

    def _axis_moved_cb(self, joy, axis, value):
        if axis in self.settings:
            self.emit_action(C.TEST_SETTINGS[axis], value=U.abs(value))

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

    def on_quit(self, *args):
        self.manager.disconnect_all()
        self.quit()


if __name__ == "__main__":
    app = XJoyApp()
    app.run(sys.argv)
