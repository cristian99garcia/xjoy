#!/usr/bin/env python
# -*- coding: utf-8 -*-

INPUT_PATH = "/dev/input"


AXIS = {
    0x00: "x",
    0x01: "y",
    0x02: "z",
    0x03: "rx",
    0x04: "ry",
    0x05: "rz",
    0x06: "trottle",
    0x07: "rudder",
    0x08: "wheel",
    0x09: "gas",
    0x0a: "brake",
    0x10: "hat0x",
    0x11: "hat0y",
    0x12: "hat1x",
    0x13: "hat1y",
    0x14: "hat2x",
    0x15: "hat2y",
    0x16: "hat3x",
    0x17: "hat3y",
    0x18: "pressure",
    0x19: "distance",
    0x1a: "tilt_x",
    0x1b: "tilt_y",
    0x1c: "tool_width",
    0x20: "volume",
    0x28: "misc",
}

BUTTONS = {
    0x120: "trigger",
    0x121: "thumb",
    0x122: "thumb2",
    0x123: "top",
    0x124: "top2",
    0x125: "pinkie",
    0x126: "base",
    0x127: "base2",
    0x128: "base3",
    0x129: "base4",
    0x12a: "base5",
    0x12b: "base6",
    0x12f: "dead",
    0x130: "a",
    0x131: "b",
    0x132: "c",
    0x133: "x",
    0x134: "y",
    0x135: "z",
    0x136: "tl",
    0x137: "tr",
    0x138: "tl2",
    0x139: "tr2",
    0x13a: "select",
    0x13b: "start",
    0x13c: "mode",
    0x13d: "thumbl",
    0x13e: "thumbr",

    0x220: "dpad_up",
    0x221: "dpad_down",
    0x222: "dpad_left",
    0x223: "dpad_right",

    # XBox 360 controller uses these codes.
    0x2c0: "dpad_left",
    0x2c1: "dpad_right",
    0x2c2: "dpad_up",
    0x2c3: "dpad_down",
}


PLAYSTATION_BUTTON_NAMES = [
    "x",
    "circle",
    "triangle",
    "square",
    "l1",
    "trigger-left",
    "r1",
    "trigger-right",
    "select",
    "start",
    "l3",
    "r3"
]


PLAYSTATION_MAP = {
    "triangle": (526, 83),
    "circle": (576, 134),
    "x": (526, 185),
    "square": (475, 134),
    "start": (386, 158),
    "select": (263, 159),
    "trigger-left": (0, 0),
    "trigger-right": (593, 0),
    "l3": (220, 238),
    "r3": (420, 238),
    "l1": (99, 0),
    "r1": (506, 0),
    "left-stick": (197, 216),
    "right-stick": (397, 216),
    "dpad": (86, 103),
}


FRONT_OBJECTS = [
    "l3",
    "r3"
]


class ActionType:
    MOUSE = 0
    KEYBOARD = 1


class MouseActionType:
    CLICK = 0
    MOVE_X = 1
    MOVE_Y = 2
    SCROLL_H = 3
    SCROLL_V = 4


class ActionState:
    OFF = 0
    ON = 1


class Action:

    def __init__(self, type, data=[]):
        self.type = type
        self.data = data


TEST_SETTINGS = {
    "x": Action(ActionType.MOUSE, [MouseActionType.MOVE_X, 10]),
    "y": Action(ActionType.MOUSE, [MouseActionType.MOVE_Y, 10]),
    289: Action(ActionType.MOUSE, [MouseActionType.CLICK, 2]),          # Circle
    290: Action(ActionType.MOUSE, [MouseActionType.CLICK, 1]),          # X
    "rz": Action(ActionType.MOUSE, [MouseActionType.SCROLL_V, 1])
}


class Direction:
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    NONE = "none"
