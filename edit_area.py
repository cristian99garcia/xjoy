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
        self.id = None

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


class Directional(DrawableObject):

    def __init__(self):
        DrawableObject.__init__(self)

        self.direction = None
        self.x = 0
        self.y = 0
        self.setting = None
        self.id = {
            "x": None,
            "y": None
        }

        self.images = {
            C.Direction.NONE: None,
            C.Direction.UP: None,
            C.Direction.RIGHT + C.Direction.UP: None,
            C.Direction.RIGHT: None,
            C.Direction.RIGHT + C.Direction.DOWN: None,
            C.Direction.DOWN: None,
            C.Direction.LEFT + C.Direction.DOWN: None,
            C.Direction.LEFT: None,
            C.Direction.SETTING_X: None,
            C.Direction.SETTING_Y: None
        }

    def set_direction(self, direction):
        if self.direction == direction:
            return

        self.direction = direction
        if self.direction in self.images.keys():
            self.set_image(self.images[self.direction])

    def get_direction(self):
        return self.direction

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


class Stick(Directional):

    def __init__(self, name):
        Directional.__init__(self)

        self.images[C.Direction.NONE]                     = Image.new_from_name("stick")
        self.images[C.Direction.UP]                       = Image.new_from_name("stick-up")
        self.images[C.Direction.RIGHT + C.Direction.UP]   = Image.new_from_name("stick-right-up")
        self.images[C.Direction.RIGHT]                    = Image.new_from_name("stick-right")
        self.images[C.Direction.RIGHT + C.Direction.DOWN] = Image.new_from_name("stick-right-down")
        self.images[C.Direction.DOWN]                     = Image.new_from_name("stick-down")
        self.images[C.Direction.LEFT + C.Direction.DOWN]  = Image.new_from_name("stick-left-down")
        self.images[C.Direction.LEFT]                     = Image.new_from_name("stick-left")
        self.images[C.Direction.LEFT + C.Direction.UP]    = Image.new_from_name("stick-left-up")
        self.images[C.Direction.SETTING_X]                = Image.new_from_name("stick-setting-x")
        self.images[C.Direction.SETTING_Y]                = Image.new_from_name("stick-setting-y")

        if name in C.PLAYSTATION_MAP.keys():
            self.rect.set_pos(*C.PLAYSTATION_MAP[name])

        self.set_image(self.images[C.Direction.NONE])


class DPad(Directional):

    def __init__(self):
        Directional.__init__(self)

        self.images[C.Direction.NONE]                     = Image.new_from_name("dpad")
        self.images[C.Direction.UP]                       = Image.new_from_name("dpad-up")
        self.images[C.Direction.RIGHT + C.Direction.UP]   = Image.new_from_name("dpad-right-up")
        self.images[C.Direction.RIGHT]                    = Image.new_from_name("dpad-right")
        self.images[C.Direction.RIGHT + C.Direction.DOWN] = Image.new_from_name("dpad-right-down")
        self.images[C.Direction.DOWN]                     = Image.new_from_name("dpad-down")
        self.images[C.Direction.LEFT + C.Direction.DOWN]  = Image.new_from_name("dpad-left-down")
        self.images[C.Direction.LEFT]                     = Image.new_from_name("dpad-left")
        self.images[C.Direction.LEFT + C.Direction.UP]    = Image.new_from_name("dpad-left-up")
        self.images[C.Direction.SETTING_X]                = Image.new_from_name("dpad-setting-x")
        self.images[C.Direction.SETTING_Y]                = Image.new_from_name("dpad-setting-y")

        if "dpad" in C.PLAYSTATION_MAP:
            self.rect.set_pos(*C.PLAYSTATION_MAP["dpad"])

        self.set_image(self.images[C.Direction.NONE])


class DrawableJoystick(GObject.GObject):

    __gsignals__ = {
        "redraw": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
        "finished-settings": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.joystick = None
        self.background = GdkPixbuf.Pixbuf.new_from_file(U.get_gamepad_image("generic"))

        self.objects = {}
        self.setting = False
        self.object_ids = {}
        self.current_object = None

        for name in C.PLAYSTATION_OBJECT_NAMES[:-3]:
            self.objects[name] = SpecialDrawableButton(name)

        for name in C.PLAYSTATION_OBJECT_NAMES[-2:]:  # ["left-stick", "right-stick"]:
            self.objects[name] = Stick(name)

        self.objects["dpad"] = DPad()

        for name in self.objects.keys():
            self.objects[name].connect("redraw", self._redraw_cb)

    @classmethod
    def new_from_joystick(self, joy):
        drawable = DrawableJoystick()
        drawable.set_joystick(joy)

        return drawable

    def set_joystick(self, joy):
        if self.joystick is not None:
            # TODO: disconnect
            pass

        self.joystick = joy
        self.joystick.connect("button-pressed", self._pressed_cb)
        self.joystick.connect("button-released", self._released_cb)
        self.joystick.connect("axis-moved", self._axis_moved_cb)

    def set_setting(self, setting):
        self.setting = setting

        if self.setting:
            self.current_object = C.PLAYSTATION_OBJECT_NAMES[0]

            for name in C.PLAYSTATION_OBJECT_NAMES:
                if self.current_object == name:
                    self.objects[name].set_pressed(True)

        else:
            self.current_object = None

    def _redraw_cb(self, object):
        self.emit("redraw")  # TODO: send a region to redraw

    def _pressed_cb(self, joy, button):
        if self.setting:
            if self.current_object is None:
                self.current_object = C.PLAYSTATION_OBJECT_NAMES[0]
                index = 1

            else:
                index = C.PLAYSTATION_OBJECT_NAMES.index(self.current_object) + 1

            if index >= C.PLAYSTATION_OBJECT_NAMES.index("dpad"):
                if index == C.PLAYSTATION_OBJECT_NAMES.index("dpad"):
                    # Start movements controls (dpads and sticks)
                    self.objects["dpad"].set_direction(C.Direction.SETTING_X)
                    self.objects[self.current_object].set_pressed(False)
                    self.current_object = C.PLAYSTATION_OBJECT_NAMES[index]

                return

            self.objects[self.current_object].set_pressed(False)
            self.objects[self.current_object].id = button
            self.object_ids[self.current_object] = button

            self.current_object = C.PLAYSTATION_OBJECT_NAMES[index]
            self.objects[self.current_object].set_pressed(True)

            return

        for name in self.objects:
            if self.objects[name].id == button:
                self.objects[name].set_pressed(True)
                break

    def _released_cb(self, joy, button):
        if self.setting:
            return

        for obj in self.objects.values():
            if obj.id == button:
                obj.set_pressed(False)
                break

    def get_directional_from_axis(self, axis):
        for _object in self.objects.values():
            if issubclass(_object.__class__, Directional):
                if _object.id["x"] == axis:
                    return _object, "x"

                elif _object.id["y"] == axis:
                    return _object, "y"

        return None, None

    def _axis_moved_cb(self, joy, axis, value):
        if axis == "z":  # FIXME: Should ignore it? or is my joystick just broken? 
            return

        if self.setting:
            if self.current_object is None:
                return

            index = C.PLAYSTATION_OBJECT_NAMES.index(self.current_object) + 1

            if index < C.PLAYSTATION_OBJECT_NAMES.index("dpad"):
                return

            if value in [-1, 1]:
                _object, direction = self.get_directional_from_axis(axis)
                if _object is not None:
                    # Already setted, prevents set the same stick/dpad
                    return

                direction = self.objects[self.current_object].get_direction()

                if direction == C.Direction.SETTING_X:
                    # If direction == X, set it to Y and wait
                    self.objects[self.current_object].id["x"] = axis
                    self.objects[self.current_object].set_direction(C.Direction.SETTING_Y)

                    self.object_ids[self.current_object] = self.objects[self.current_object].id

                elif direction == C.Direction.SETTING_Y:
                    # If direction == Y, continue with the next directional object or
                    # finish the configuration, it depends if the current setting
                    # directional object is the last object
                    self.objects[self.current_object].id["y"] = axis
                    self.objects[self.current_object].set_direction(C.Direction.NONE)

                    self.object_ids[self.current_object] = self.objects[self.current_object].id

                    if index == len(C.PLAYSTATION_OBJECT_NAMES):
                        self.setting = False
                        self.emit("finished-settings")

                    else:
                        self.current_object = C.PLAYSTATION_OBJECT_NAMES[index]
                        self.objects[self.current_object].set_direction(C.Direction.SETTING_X)

            return

        _object, direction = self.get_directional_from_axis(axis)
        if _object is not None:
            if direction == "x":
                _object.set_x(value)

            elif direction == "y":
                _object.set_y(value)

        return

    def get_objects(self):
        return self.object_ids

    def set_objects(self, objects):
        self.setting = False
        self.object_ids = objects

        for key in self.object_ids.keys():
            self.objects[key].id = self.object_ids[key]


class EditArea(Gtk.DrawingArea):

    __gsignals__ = {
        "finished-settings": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.connect("draw", self._draw_cb)
        self.set_size_request(690, 428)  # Image size

        self.drawable = None
        self.setting = False

        self.objects = []
        self.objects_ids = {}

        self.show_all()

    def _draw_cb(self, widget, context):
        if self.drawable is None:
            return

        Gdk.cairo_set_source_pixbuf(context, self.drawable.background, 0, 7)
        context.paint()

        for name in self.objects:
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
            return

        if self.drawable is not None:
            # TODO: disconnect signals
            pass

        if self.drawable is None or joy.file != self.drawable.joystick.file:
            self.drawable = DrawableJoystick.new_from_joystick(joy)

            self.objects = self.drawable.objects.keys()
            for name in C.FRONT_OBJECTS:
                self.objects.remove(name)
                self.objects.insert(-1, name)

            self.drawable.set_setting(self.setting)
            self.drawable.set_objects(self.objects_ids)

            self.drawable.connect("redraw", self._redraw_cb)
            self.drawable.connect("finished-settings", lambda d: self.emit("finished-settings"))
            self.redraw()

    def _redraw_cb(self, drawable):
        self.redraw()

    def set_setting(self, setting):
        self.setting = setting

        if self.drawable is not None:
            self.drawable.set_setting(setting)

    def get_objects(self):
        return self.drawable.get_objects()

    def set_objects(self, objects):
        self.objects_ids = objects

        if self.drawable is not None:
            self.drawable.set_objects(objects)
