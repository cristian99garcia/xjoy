#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import array
import fcntl

from gi.repository import GdkPixbuf

import consts as C


def get_device_name(devfile):
    buf = array.array("c", ["\0"] * 64)
    fcntl.ioctl(devfile, 0x80006a13 + (0x10000 * len(buf)), buf)

    return buf.tostring()


def get_joystick_axes(devfile):
    buf = array.array("B", [0])
    fcntl.ioctl(devfile, 0x80016a11, buf)

    return buf[0]


def get_joystick_buttons(devfile):
    buf = array.array("B", [0])
    fcntl.ioctl(devfile, 0x80016a12, buf)

    return buf[0]


def get_joystick_axis_map(devfile):
    axis_map = []
    axis_states = {}

    buf = array.array("B", [0] * 0x40)
    fcntl.ioctl(devfile, 0x80406a32, buf)

    for axis in buf[:get_joystick_axes(devfile)]:
        axis_name = C.AXIS.get(axis, "unknown(0x%02x)" % axis)
        axis_map.append(axis_name)
        axis_states[axis_name] = 0.0

    return axis_map, axis_states


def get_joystick_button_map(devfile):
    button_map = []
    button_states = {}

    buf = array.array("H", [0] * 200)
    fcntl.ioctl(devfile, 0x80406a34, buf)

    for button in buf[:get_joystick_buttons(devfile)]:
        # btn_name = button  # C.BUTTONS.get(button, "unknown(0x%03x)" % button)
        button_map.append(button)
        button_states[button] = 0

    return button_map, button_states


def get_local_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_gamepad_image(name):
    return os.path.join(get_local_dir(), "data", "gamepads", name + ".png")


def get_drawable_image(name, resp_name=None):
    file = os.path.join(get_local_dir(), "data", "icons", name + ".png")
    if os.path.exists(file):
        return file

    if resp_name is not None:
        return get_drawable_image(resp_name)

    else:
        # Error
        return None


def get_app_icon_file():
    return os.path.join(get_local_dir(), "data", "icons", "xjoy.svg")


def get_app_icon_pixbuf(width=210, height=210):
    return GdkPixbuf.Pixbuf.new_from_file_at_size(get_app_icon_file(), width, height)


def get_tray_icon_file():
    return os.path.join(get_local_dir(), "data", "icons", "xjoy-trayicon.svg")


def abs(value):
    if value > 0:
        return 1

    elif value < 0:
        return -1

    return 0


def invert_abs(value):
    value = abs(value)

    if value > 0:
        return -1

    elif value < 0:
        return 1

    return 0


def event_type_to_str(action):
    return "%d:%d" % (action.type, action.data[0])


def str_to_event_type(value):
    numbers = value.split(":")
    return int(numbers[0]), int(numbers[1])


def load_settings_from_file(_file):
    """
    Convert a saved dict to a ready to use dict.

    Settings structure:
    {
        "objects": {
            BUTTON_NAME: id,
            DIRECTIONAL_NAME: {
                "x": id,
                "y": id
            }
        },
        "actions": {
            EVENT_NAME: {
                "type": EVENT_TYPE,
                "data": DATA
            },
            EVENT_NAME: {
                "type": EVENT_TYPE,
                "data": DATA
            },
            EVENT_NAME: {
                "type": EVENT_TYPE,
                "data": DATA
            }
        }
    }

    EVENT_TYPE structure:
    DEVICE_TYPE:EVENT

    DATA structure:
    [
        ACTION_TYPE,
        VALUE,
        VALUE,
        VALUE
    ]
    """

    data = {}
    converted = {}

    with open(_file, "r") as file:
        data = json.loads(file.read())

    objects = data["objects"]
    actions = data["actions"]

    for key in actions.keys():
        name = str(key)
        device, event_type = str_to_event_type(actions[name]["type"])
        if name.isdigit():
            name = int(name)

        converted[name] = C.Action(device, [event_type] + actions[key]["data"])

    return converted, objects


def convert_settings(settings, objects):
    """
    Convert a settings dict to a ready to save dict
    """
    converted = {
        "actions": {},
        "objects": objects,
    }

    for key in settings.keys():
        # key = EVENT_NAME
        action = settings[key]

        converted["actions"][key] = {
            "type": event_type_to_str(action),
            "data": action.data[1:]
        }

    return converted


def save_settings(settings, _file):
    """
    WARNING: convert settings first
    """

    data = json.dumps(settings, indent=4, separators=(",", ": "))

    with open(_file, "w") as file:
        file.write(data)
