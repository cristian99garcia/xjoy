#!/usr/bin/env python
# -*- coding: utf-8 -*-

def display_manager(display):
    from contextlib import contextmanager

    @contextmanager
    def manager():
        errors = []

        def handler(*args):
            errors.append(args)

        old_handler = display.set_error_handler(handler)
        yield display
        display.sync()
        display.set_error_handler(old_handler)
        if errors:
            #raise X11Error(errors)
            pass

    return manager()


def translate_button_code(button):
    # In X11, the button numbers are:
    #  leftclick=1, middleclick=2, rightclick=3
    #  For the purposes of the cross-platform interface of PyMouse, we
    #  invert the button number values of the right and middle buttons
    if button in [1, 2, 3]:
        return (None, 1, 3, 2)[button]

    else:
        return button
