#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils as U
import consts as C

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf


class Rect:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    @classmethod
    def new_from_data(self, x=0, y=0, width=0, height=0):
        rect = Rect()
        rect.x = x if x is not None else 0
        rect.y = y if y is not None else 0
        rect.width = width if width is not None else 0
        rect.height = height if height is not None else 0

        return rect

    def set_pos(self, x=None, y=None):
        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y

    def set_size(self, width=None, height=None):
        self.width = width if width is not None else self.width
        self.height = height if height is not None else self.height


class Image:

    def __init__(self):
        self.file = None
        self.pixbuf = None
        self.width = 0
        self.height = 0

    @classmethod
    def new_from_file(self, file):
        image = Image()
        image.file = file
        image.pixbuf = GdkPixbuf.Pixbuf.new_from_file(image.file)
        image.width = image.pixbuf.get_width()
        image.height = image.pixbuf.get_height()

        return image

    @classmethod
    def new_from_name(self, name, resp_name=None):
        return Image.new_from_file(U.get_drawable_image(name, resp_name))


class DrawableObject(GObject.GObject):

    __gsignals__ = {
        "redraw": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.rect = Rect()
        self.image = None

    def set_image(self, image, x=None, y=None):
        del self.image
        self.image = image

        self.rect.set_pos(x, y)

        if self.image is not None:
            self.rect.set_size(self.image.width, self.image.height)

        self.emit("redraw")


class DrawableButton(DrawableObject):

    def __init__(self, default=True):
        DrawableObject.__init__(self)

        self.pressed = False
        self.ireleased = None
        self.ipressed = None

        if default:
            self.ireleased = Image.new_from_name("button")
            self.ipressed = Image.new_from_name("button-activated")
            self.set_image(self.ireleased)

    def set_pressed(self, pressed):
        if pressed == self.pressed:
            return

        self.pressed = pressed
        if self.pressed:
            self.set_image(self.ipressed)

        else:
            self.set_image(self.ireleased)


class SpecialDrawableButton(DrawableButton):

    def __init__(self, name):
        DrawableButton.__init__(self, False)

        if name in C.PLAYSTATION_MAP:
            self.rect.set_pos(*C.PLAYSTATION_MAP[name])

        if "trigger" in name:
            name = "trigger"

        self.ireleased = Image.new_from_name(name, "button")
        self.ipressed = Image.new_from_name(name + "-pressed", "button-pressed")

        self.set_image(self.ireleased)


class Direccional(DrawableObject):

    def __init__(self):
        DrawableObject.__init__(self)

        self.direction = None
        self.x = 0
        self.y = 0

        self.images = {
            C.Direction.NONE: None,
            C.Direction.UP: None,
            C.Direction.RIGHT + C.Direction.UP: None,
            C.Direction.RIGHT: None,
            C.Direction.RIGHT + C.Direction.DOWN: None,
            C.Direction.DOWN: None,
            C.Direction.LEFT + C.Direction.DOWN: None,
            C.Direction.LEFT: None
        }

    def set_direction(self, direction):
        if self.direction == direction:
            return

        self.direction = direction
        if self.direction in self.images.keys():
            self.set_image(self.images[self.direction])

    def set_x(self, x=0):
        if self.x == U.abs(x):
            return

        self.x = U.abs(x)
        self.reset_direction_from_xy()

    def set_y(self, y=0):
        if self.y == U.abs(y):
            return

        self.y = U.abs(y)
        self.reset_direction_from_xy()

    def reset_direction_from_xy(self):
        if self.x == 0:
            if self.y == 0:
                self.set_direction(C.Direction.NONE)

            elif self.y < 0:
                self.set_direction(C.Direction.UP)

            elif self.y > 0:
                self.set_direction(C.Direction.DOWN)

        elif self.x < 0:
            if self.y == 0:
                self.set_direction(C.Direction.LEFT)

            elif self.y < 0:
                self.set_direction(C.Direction.LEFT + C.Direction.UP)

            elif self.y > 0:
                self.set_direction(C.Direction.LEFT + C.Direction.DOWN)

        elif self.x > 0:
            if self.y == 0:
                self.set_direction(C.Direction.RIGHT)

            elif self.y < 0:
                self.set_direction(C.Direction.RIGHT + C.Direction.UP)

            elif self.y > 0:
                self.set_direction(C.Direction.RIGHT + C.Direction.DOWN)


class Stick(Direccional):

    def __init__(self, name):
        Direccional.__init__(self)

        self.images[C.Direction.NONE] =                     Image.new_from_name("stick")
        self.images[C.Direction.UP] =                       Image.new_from_name("stick-up")
        self.images[C.Direction.RIGHT + C.Direction.UP] =   Image.new_from_name("stick-right-up")
        self.images[C.Direction.RIGHT] =                    Image.new_from_name("stick-right")
        self.images[C.Direction.RIGHT + C.Direction.DOWN] = Image.new_from_name("stick-right-down")
        self.images[C.Direction.DOWN] =                     Image.new_from_name("stick-down")
        self.images[C.Direction.LEFT + C.Direction.DOWN] =  Image.new_from_name("stick-left-down")
        self.images[C.Direction.LEFT] =                     Image.new_from_name("stick-left")
        self.images[C.Direction.LEFT + C.Direction.UP] =    Image.new_from_name("stick-left-up")

        if name in C.PLAYSTATION_MAP.keys():
            self.rect.set_pos(*C.PLAYSTATION_MAP[name])

        self.set_image(self.images[C.Direction.NONE])


class DPad(Direccional):

    def __init__(self):
        Direccional.__init__(self)

        self.images[C.Direction.NONE] =                     Image.new_from_name("dpad")
        self.images[C.Direction.UP] =                       Image.new_from_name("dpad-up")
        self.images[C.Direction.RIGHT + C.Direction.UP] =   Image.new_from_name("dpad-right-up")
        self.images[C.Direction.RIGHT] =                    Image.new_from_name("dpad-right")
        self.images[C.Direction.RIGHT + C.Direction.DOWN] = Image.new_from_name("dpad-right-down")
        self.images[C.Direction.DOWN] =                     Image.new_from_name("dpad-down")
        self.images[C.Direction.LEFT + C.Direction.DOWN] =  Image.new_from_name("dpad-left-down")
        self.images[C.Direction.LEFT] =                     Image.new_from_name("dpad-left")
        self.images[C.Direction.LEFT + C.Direction.UP] =    Image.new_from_name("dpad-left-up")

        if "dpad" in C.PLAYSTATION_MAP:
            self.rect.set_pos(*C.PLAYSTATION_MAP["dpad"])

        self.set_image(self.images[C.Direction.NONE])


class DrawableJoystick(GObject.GObject):

    __gsignals__ = {
        "redraw": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.joystick = None
        self.background = GdkPixbuf.Pixbuf.new_from_file(U.get_gamepad_image("generic"))

        self.objects = {}

        for name in C.TRANSLATED_BUTTONS.values():
            self.objects[name] = SpecialDrawableButton(name)

        for stick in ["left-stick", "right-stick"]:
            self.objects[stick] = Stick(stick)

        self.objects["dpad"] = DPad()

        for name in self.objects.keys():
            self.objects[name].connect("redraw", self._redraw_cb)

    @classmethod
    def new_from_joystick(self, joy):
        drawable = DrawableJoystick()
        drawable.set_joystick(joy)

        #print drawable.joystick.axis_map
        return drawable

    def set_joystick(self, joy):
        if self.joystick is not None:
            # TODO: disconnect
            pass

        self.joystick = joy
        self.joystick.connect("button-pressed", self._pressed_cb)
        self.joystick.connect("button-released", self._released_cb)
        self.joystick.connect("axis-moved", self._axis_moved_cb)

    def _redraw_cb(self, object):
        self.emit("redraw")  # TODO: send a region to redraw

    def _pressed_cb(self, joy, button):
        if button in C.TRANSLATED_BUTTONS:
            name = C.TRANSLATED_BUTTONS[button]

            self.objects[name].set_pressed(True)

    def _released_cb(self, joy, button):
        if button in C.TRANSLATED_BUTTONS:
            name = C.TRANSLATED_BUTTONS[button]
            self.objects[name].set_pressed(False)

    def _axis_moved_cb(self, joy, axis, value):
        if axis == "x":
            self.objects["left-stick"].set_x(value)

        elif axis == "y":
            self.objects["left-stick"].set_y(value)

        elif axis == "rx":
            self.objects["right-stick"].set_x(value)

        elif axis == "rz":
            self.objects["right-stick"].set_y(value)

        elif axis == "hat0x":
            self.objects["dpad"].set_x(value)

        elif axis == "hat0y":
            self.objects["dpad"].set_y(value)


class EditArea(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.connect("draw", self._draw_cb)
        self.set_size_request(690, 428)  # Image size

        self.drawable = None

        self.show_all()

    def _draw_cb(self, widget, context):
        if self.drawable is None:
            return

        Gdk.cairo_set_source_pixbuf(context, self.drawable.background, 0, 7)
        context.paint()

        list = self.drawable.objects.keys()
        for name in C.FRONT_OBJECTS:
            list.remove(name)
            list.insert(-1, name)

        for name in list:
            self.draw_object(context, self.drawable.objects[name])

    def draw_object(self, context, object):
        if object.image is None or object.image.pixbuf is None:
            return

        Gdk.cairo_set_source_pixbuf(context, object.image.pixbuf, object.rect.x, object.rect.y)
        context.paint()

    def redraw(self):
        GLib.idle_add(self.queue_draw)

    def set_joystick(self, joy):
        if joy is None:
            self.drawable = None
            self.redraw()
            return

        if self.drawable is not None:
            # TODO: disconnect signals
            pass

        if self.drawable is None or joy.file != self.drawable.joystick.file:
            self.drawable = DrawableJoystick.new_from_joystick(joy)
            self.drawable.connect("redraw", self._redraw_cb)
            self.redraw()

    def _redraw_cb(self, drawable):
        self.redraw()
