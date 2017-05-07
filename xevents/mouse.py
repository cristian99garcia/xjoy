#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input

import utils as U

class Mouse():

    def __init__(self, display=":0"):
        self.display = Display(":0")

    def position(self):
        coord = self.display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]

    def move(self, x, y):
        if (x, y) != self.position():
            with U.display_manager(self.display) as d:
                fake_input(d, X.MotionNotify, x=x, y=y)

    def press(self, x=None, y=None, button=1):
        if x is not None and y is not None:
            self.move(x, y)

        with U.display_manager(self.display) as display:
            fake_input(display, X.ButtonPress, U.translate_button_code(button))

    def release(self, x=None, y=None, button=1):
        if x is not None and y is not None:
            self.move(x, y)

        with U.display_manager(self.display) as display:
            fake_input(display, X.ButtonRelease, U.translate_button_code(button))

    def click(self, x=None, y=None, button=1, n=1):
        for i in range(n):
            self.press(x, y, button)
            self.release(x, y, button)

    def scroll(self, vertical=None, horizontal=None):
        if vertical is not None:
            vertical = int(vertical)
            if vertical == 0:
                pass

            elif vertical > 0:
                self.click(*self.position(), button=4, n=vertical)

            else:
                self.click(*self.position(), button=5, n=abs(vertical))

        if horizontal is not None:
            horizontal = int(horizontal)
            if horizontal == 0:
                pass

            elif horizontal > 0:
                self.click(button=7, n=horizontal)

            else:
                self.click(button=6, n=abs(horizontal))
