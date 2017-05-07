#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
import os
import sys

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk
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


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_size_request(690, 428)
        self.set_resizable(False)
        self.set_title("XJoy")
        self.connect("delete-event", self._exit)

        self.mouse_direction = [0, 0]
        self.scroll_direction = [0, 0]
        self.mouse_movement_id = None
        self.scroll_id = None

        if TESTING:
            self.settings = C.TEST_SETTINGS
        
        else:
            self.settings = {}

        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.manager = JoysticksManager()
        self.manager.connect("joysticks-changed", self._joys_changed_cb)

        self.edit_area = EditArea()
        self.add(self.edit_area)

        self.manager.start()
        self.show_all()

    def _joys_changed_cb(self, manager):
        joys = manager.get_connected_joysticks()

        joystick = joys[0]  # TODO: que el usuario elija
        joystick.connect("button-pressed", self._pressed_cb)
        joystick.connect("button-released", self._released_cb)
        joystick.connect("axis-moved", self._axis_moved_cb)

        self.edit_area.set_joystick(joystick)

    def _exit(self, window, event):
        self.manager.disconnect_all()
        Gtk.main_quit()

        return False

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


if __name__ == "__main__":
    MainWindow()
    Gtk.main()
