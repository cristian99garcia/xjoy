#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import Xlib.XK
from Xlib.display import Display
from Xlib.ext.xtest import fake_input
from Xlib import X
import Xlib.keysymdef.xkb

import utils as U
import consts as C


class Keyboard():

    def __init__(self, display=":0"):

        self.display = Display(display)
        self.load_special_keys()

    def load_special_keys(self):
        self.BACKSPACE = self.lookup_character_keycode("BackSpace")
        self.TAB = self.lookup_character_keycode("Tab")
        self.LINE_FEED = self.lookup_character_keycode("Linefeed")
        self.CLEAR = self.lookup_character_keycode("Clear")
        self.RETURN = self.lookup_character_keycode("Return")
        self.ENTER = self.RETURN
        self.PAUSE = self.lookup_character_keycode("Pause")
        self.SCROLL_LOCK = self.lookup_character_keycode("Scroll_Lock")
        self.SYS_REQ = self.lookup_character_keycode("Sys_Req")
        self.ESCAPE = self.lookup_character_keycode("Escape")
        self.DELETE = self.lookup_character_keycode("Delete")

        #Modifier Keys
        self.SHIFT_L = self.lookup_character_keycode("Shift_L")
        self.SHIFT_R = self.lookup_character_keycode("Shift_R")
        self.SHIFT = self.SHIFT_L  # Default Shift is left Shift
        self.ALT_L = self.lookup_character_keycode("Alt_L")
        self.ALT_R = self.lookup_character_keycode("Alt_R")
        self.ALTGR = self.lookup_character_keycode("ISO_Level3_Shift")
        self.ALT = self.ALT_L  # Default Alt is left Alt
        self.CONTROL_L = self.lookup_character_keycode("Control_L")
        self.CONTROL_R = self.lookup_character_keycode("Control_R")
        self.CONTROL = self.CONTROL_L  # Default Ctrl is left Ctrl
        self.CAPS_LOCK = self.lookup_character_keycode("Caps_Lock")
        self.CAPITAL = self.CAPS_LOCK  # Some may know it as Capital
        self.SHIFT_LOCK = self.lookup_character_keycode("Shift_Lock")
        self.META_L = self.lookup_character_keycode("Meta_L")
        self.META_R = self.lookup_character_keycode("Meta_R")
        self.SUPER_L = self.lookup_character_keycode("Super_L")
        self.WINDOWS_L = self.SUPER_L  # Cross-support; also it"s printed there
        self.SUPER_R = self.lookup_character_keycode("Super_R")
        self.WINDOWS_R = self.SUPER_R  # Cross-support; also it"s printed there
        self.HYPER_L = self.lookup_character_keycode("Hyper_L")
        self.HYPER_R = self.lookup_character_keycode("Hyper_R")

        #Cursor Control and Motion
        self.HOME = self.lookup_character_keycode("Home")
        self.UP = self.lookup_character_keycode("Up")
        self.DOWN = self.lookup_character_keycode("Down")
        self.LEFT = self.lookup_character_keycode("Left")
        self.RIGHT = self.lookup_character_keycode("Right")
        self.END = self.lookup_character_keycode("End")
        self.BEGIN = self.lookup_character_keycode("Begin")
        self.PAGE_UP = self.lookup_character_keycode("Page_Up")
        self.PAGE_DOWN = self.lookup_character_keycode("Page_Down")
        self.PRIOR = self.lookup_character_keycode("Prior")
        self.NEXT = self.lookup_character_keycode("Next")

        #Misc Functions
        self.SELECT = self.lookup_character_keycode("Select")
        self.PRINT = self.lookup_character_keycode("Print")
        self.PRINT_SCREEN = self.PRINT  # Seems to be the same thing
        self.SNAPSHOT = self.PRINT  # Another name for printscreen
        self.EXECUTE = self.lookup_character_keycode("Execute")
        self.INSERT = self.lookup_character_keycode("Insert")
        self.UNDO = self.lookup_character_keycode("Undo")
        self.REDO = self.lookup_character_keycode("Redo")
        self.MENU = self.lookup_character_keycode("Menu")
        self.APPS = self.MENU  # Windows...
        self.FIND = self.lookup_character_keycode("Find")
        self.CANCEL = self.lookup_character_keycode("Cancel")
        self.HELP = self.lookup_character_keycode("Help")
        self.BREAK = self.lookup_character_keycode("Break")
        self.MODE_SWITCH = self.lookup_character_keycode("Mode_switch")
        self.SCRIPT_SIWTCH = self.lookup_character_keycode("script_switch")
        self.NUM_LOCK = self.lookup_character_keycode("Num_Lock")

        #Keypad Keys: Dictionary structure
        keypad = ["Space", "Tab", "Enter", "F1", "F2", "F3", "F4", "Home",
                  "Left", "Up", "Right", "Down", "Prior", "Page_Up", "Next",
                  "Page_Down", "End", "Begin", "Insert", "Delete", "Equal",
                  "Multiply", "Add", "Separator", "Subtract", "Decimal",
                  "Divide", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        self.KEYPAD_KEYS = dict((k, self.lookup_character_keycode("KP_" + str(k))) for k in keypad)
        self.NUMPAD_KEYS = self.KEYPAD_KEYS

        #Function Keys/ Auxilliary Keys
        #FKeys
        self.FUNCTION_KEYS = [None] + [self.lookup_character_keycode("F" + str(i)) for i in range(1, 36)]
        #LKeys
        self.L_KEYS = [None] + [self.lookup_character_keycode("L" + str(i)) for i in range(1, 11)]
        #RKeys
        self.R_KEYS = [None] + [self.lookup_character_keycode("R" + str(i)) for i in range(1, 16)]

    def _handle_key(self, character, event):
        try:
            # Detect uppercase or shifted character
            shifted = self.is_char_shifted(character)

        except AttributeError:
            # Handle the case of integer keycode argument
            with U.display_manager(self.display) as display:
                fake_input(display, event, character)

        else:
            with U.display_manager(self.display) as display:
                if shifted:
                    fake_input(display, event, self.SHIFT)

                keycode = self.lookup_character_keycode(character)
                fake_input(display, event, keycode)

    def press_key(self, character=""):
        self._handle_key(character, X.KeyPress)

    def release_key(self, character=""):
        self._handle_key(character, X.KeyRelease)

    def is_char_shifted(self, character):
        if character.isupper():
            return True

        if character in "<>?:\"{}|~!@#$%^&*()_+":
            return True

        return False

    def type_string(self, char_string, interval=0):
        shift = False
        for char in char_string:
            if self.is_char_shifted(char):
                if not shift:  # Only press Shift as needed
                    time.sleep(interval)
                    self.press_key(self.SHIFT)
                    shift = True

                if char in "<>?:\"{}|~!@#$%^&*()_+":
                    ch_index = "<>?:\"{}|~!@#$%^&*()_+".index(char)
                    unshifted_char = ",./;'[]\\`1234567890-="[ch_index]

                else:
                    unshifted_char = char.lower()

                time.sleep(interval)
                self.tap_key(unshifted_char)

            else:  # Unshifted already
                if shift and char != " ":  # Only release Shift as needed
                    self.release_key(self.SHIFT)
                    shift = False

                time.sleep(interval)
                self.tap_key(char)

        if shift:
            self.release_key(self.SHIFT)

    def tap_key(self, character="", n=1, interval=0):
        for i in range(n):
            self.press_key(character)
            self.release_key(character)
            time.sleep(interval)

    def lookup_character_keycode(self, character):
        keysym = Xlib.XK.string_to_keysym(character)
        if not keysym:
            try:
                keysym = getattr(Xlib.keysymdef.xkb, "XK_" + character, 0)

            except:
                keysym = 0

        if not keysym:
            keysym = Xlib.XK.string_to_keysym(C.KEYSYMS[character])

        return self.display.keysym_to_keycode(keysym)


if __name__ == "__main__":
    k = Keyboard()
    k.tap_key("l")
