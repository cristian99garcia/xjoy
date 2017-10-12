#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import array
import fcntl

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

    for btn in buf[:get_joystick_buttons(devfile)]:
        btn_name = C.BUTTONS.get(btn, "unknown(0x%03x)" % btn)
        button_map.append(btn_name)
        button_states[btn_name] = 0

    return button_map, button_states


def get_gamepad_image(name):
    return os.path.join(os.path.dirname(__file__), "data", "gamepads", name + ".png")


def get_drawable_image(name, resp_name=None):
    file = os.path.join(os.path.dirname(__file__), "data", "icons", name + ".png")
    if os.path.exists(file):
        return file

    if resp_name is not None:
        return get_drawable_image(resp_name)

    else:
        # Error
        return None


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

    for key in data:
        device, event_type = str_to_event_type(data[key]["type"])
        converted[str(key)] = C.Action(device, [event_type] + data[key]["data"])

    return converted


def convert_settings(settings):
    """
    Convert a settings dict to a ready to save dict
    """
    converted = {}

    for key in settings.keys():
        # key = EVENT_NAME
        action = settings[key]

        converted[key] = {
            "type": event_type_to_str(action),
            "data": action.data[1:]
        }

    return converted


def save_settings(settings, _file="test.json"):
    converted = convert_settings(settings)
    data = json.dumps(converted, indent=4, separators=(",", ": "))

    with open(_file, "w") as file:
        file.write(data)
