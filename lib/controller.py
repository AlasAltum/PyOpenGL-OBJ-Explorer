import sys

import glfw
from OpenGL.GL import *
import numpy as np


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.size = 1.0
        self.mouse_pos = (0, 0)


class Character:
    def __init__(self):
        self.position = np.zeros(3)
        self.old_pos = 0, 0
        self.theta = np.pi * 0.5
        self.phi = 0.0
        self.mouse_sensitivity = 1.0

    def update_angle(self, dx, dz, dt):
        # multiplo_inicial = self.theta // np.pi

        self.phi -= dx * dt * self.mouse_sensitivity
        theta_0 = self.theta

        dtheta = dz * dt * self.mouse_sensitivity
        self.theta += dtheta

        if self.theta < 0:
            self.theta = 0.01

        elif self.theta > np.pi:
            self.theta = 3.14159

        else:
            pass

        # if (self.theta + dtheta) // np.pi == multiplo_inicial:
        #     self.theta += dtheta

        return self.phi, self.theta

    def move(self, window, viewPos, forward, new_side, dt):

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position[0] -= 2 * dt
            viewPos += new_side * dt * 10

        elif glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position[0] += 2 * dt
            viewPos -= new_side * dt * 10

        elif glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position[1] += 2 * dt
            viewPos += forward * dt * 10

        elif glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position[1] -= 2 * dt
            viewPos -= forward * dt * 10

        elif glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            self.position[2] += 2 * dt
            viewPos[2] += 2 * dt

        else:
            pass

        return self.position


# We will use the global controller as communication with the callback function
_controller = Controller()
_character = Character()


def on_key(window, key, scancode, action, mods):

    global _controller

    if key == glfw.KEY_SPACE:
        _controller.fillPolygon = not _controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    elif key == glfw.KEY_O:
        _controller.size -= 0.01

    elif key == glfw.KEY_P:
        _controller.size += 0.01


def cursor_pos_callback(window, x, y):
    global _controller
    _controller.mouse_pos = (x, y)
