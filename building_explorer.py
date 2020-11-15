# coding=utf-8

"""
Building explorer.

HOW TO: Put an OBJ file in the same directory as this script.
Run the script.
Insert the name of the obj file.
"""


import sys
import os

import glfw
import numpy as np
import OpenGL.GL.shaders
from OpenGL.GL import *

import lib.basic_shapes as bs
import lib.easy_shaders as es
import lib.lighting_shaders as ls
import lib.obj_handler as obj_reader
import lib.transformations as tr
from lib.controller import _character, _controller, cursor_pos_callback, on_key

# Execute just when this is the script called
# Not when it is imported
if __name__ == "__main__":

    # Do you want color or a texture?
    texture = int(input("Use texture?: Yes: 1, No: 0   "))
    texture = True if texture == 1 else False

    # Asking for an obj name
    obj = input("Enter the name of an obj file: ")
    # if input does not end in .obj, then add it.
    obj = (obj + ".obj") if ".obj" not in obj else obj

    if texture:
        # Asking for a texture name
        obj_texture = input("Please enter a png file: ")
        # if input does not end in .png then add it.
        obj_texture = (
            (obj_texture + ".png") if ".png" not in obj_texture else obj_texture
        )

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1200
    height = 800

    window = glfw.create_window(width, height, "Reading a *.obj file", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Connecting callback functions to handle mouse events:
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)

    # Make the mouse be always in the middle, just record movements as in FPS.
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Defining shader programs
    pipeline = (
        ls.SimpleTextureGouraudShaderProgram()
        if texture
        else ls.SimpleGouraudShaderProgram()
    )

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    try:
        if texture:
            obj_shape = obj_reader.readTextureOBJ(f"{obj}", obj_texture)
            gpuOBJ = es.toGPUShape(obj_shape, GL_REPEAT, GL_LINEAR)

        else:
            gpuOBJ = es.toGPUShape(obj_reader.readOBJ(f"{obj}", color=[0.9, 0.6, 0.2]))

    except FileNotFoundError as fe:
        print(f"File not found. Current path is: {os.getcwd()}")
        raise

    # Initializing first variables
    t0 = glfw.get_time()
    at = np.zeros(3)
    z0 = 0.0
    x0 = 0.0
    phi = np.pi * 0.25
    theta = 0
    up = np.array((0.0, 0.0, 1.0))
    viewPos = np.zeros(3)
    viewPos[2] = 2.0

    # Setting up the projection transform
    projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        x1, z1 = glfw.get_cursor_pos(window)

        dt = t1 - t0
        t0 = t1

        dz = z1 - z0
        z0 = z1

        dx = x1 - x0
        x0 = x1

        # update angles
        phi, theta = _character.update_angle(dx, dz, dt)

        # Setting up the view transform

        # Where do we look at?
        # A good way to understand this is that we would like
        # to see in fron of us in each possible angle.
        # This is what we do using spherical coordinates

        # REMAINDER:
        #  x = cos(phi) * sin(theta)
        #  y = sin(phi) * sin(theta)
        #  z = cos(theta)
        at = np.array(
            [
                np.cos(phi) * np.sin(theta),  # x
                np.sin(phi) * np.sin(theta),  # y
                np.cos(theta),  # z
            ]
        )

        phi_side = phi + np.pi * 0.5  # Simple correction

        # Side vector, this helps us define
        # our sideway movement
        new_side = np.array(
            [np.cos(phi_side) * np.sin(theta), np.sin(phi_side) * np.sin(theta), 0]
        )

        # height of our character. Where are his eyes?
        viewPos[2] = 0.8

        # We have to redefine our at and forward vectors
        # Now considering our character's position.
        new_at = at + viewPos
        forward = new_at - viewPos

        # Move character according to the given parameters
        _character.move(window, viewPos, forward, new_side, dt)

        # Setting camera look.
        view = tr.lookAt(viewPos, at + viewPos, up)  # Eye  # At  # Up

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if _controller.fillPolygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Setting shader
        glUseProgram(pipeline.shaderProgram)

        # Setting light intensity
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.7, 0.7, 0.7)

        # Setting material composition
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.7, 0.7, 0.7)

        # Setting light position, camera position, and other parameters
        # Note that the lightPosition is where we are looking at
        # The view Position is our current position.
        glUniform3f(
            glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), *viewPos
        )
        glUniform3f(
            glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), *viewPos
        )
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 1000)
        glUniform1f(
            glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001
        )
        glUniform1f(
            glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.001
        )
        glUniform1f(
            glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0011
        )

        # Setting MVP of OBJ
        glUniformMatrix4fv(
            glGetUniformLocation(pipeline.shaderProgram, "projection"),
            1,
            GL_TRUE,
            projection,
        )
        glUniformMatrix4fv(
            glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view
        )
        glUniformMatrix4fv(
            glGetUniformLocation(pipeline.shaderProgram, "model"),
            1,
            GL_TRUE,
            tr.matmul(
                [
                    tr.rotationX(np.pi / 2),
                    tr.translate(1.5, -0.25, 0),
                    tr.uniformScale(_controller.size),
                ]
            ),
        )

        # Drawing given OBJ.
        pipeline.drawShape(gpuOBJ)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
