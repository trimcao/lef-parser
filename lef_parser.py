"""
Lef Parser
Author: Tri Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from lef_util import *
from util import *
import matplotlib.pyplot as plt

"""
Note:
"""

SCALE = 2000;

# can make the stack to be an object if needed
stack = []

# store the statements info in a list
statements = []

# Now try using my data structure to parse
# open the file and start reading
path = "./libraries/FreePDK45/AND2_OR2.lef"
# path = "./libraries/FreePDK45/FreePDK45nm.lef"
f = open(path, "r+")
# the program will run until the end of file f
for line in f:
    # print (stack)
    info = str_to_list(line)
    if len(info) != 0:
        # if info is a blank line, then move to next line
        # check if the program is processing a statement
        if len(stack) != 0:
            curState = stack[len(stack) - 1]
            nextState = curState.parse_next(info)
        else:
            curState = Statement()
            nextState = curState.parse_next(info)
        # check the status return from parse_next function
        if nextState == 0:
            # continue as normal
            pass
        elif nextState == 1:
            # remove the done statement from stack, and add it to the statements
            # list
            if len(stack) != 0:
                statements.append(stack.pop())
        elif nextState == -1:
            pass
        else:
            stack.append(nextState)
            # print (nextState)
f.close()

# print parsed statements
#for each in statements:
#    if each.type == "MACRO":
#        print(each)

def draw_obs(obs, color):
    """
    Helper method to draw a OBS object
    :return: void
    """
    # process each Layer
    for layer in obs.info["LAYER"]:
        for shape in layer.shapes:
            scaled_pts = scalePts(shape.points, SCALE)
            if (shape.type == "RECT"):
                scaled_pts = rect_to_polygon(scaled_pts)
            draw_shape = plt.Polygon(scaled_pts, closed=True, fill=True,
                                color=color, edgecolor=color)
            plt.gca().add_patch(draw_shape)


def draw_port(port, color):
    """
    Helper method to draw a PORT object
    :return: void
    """
    # process each Layer
    for layer in port.info["LAYER"]:
        for shape in layer.shapes:
            scaled_pts = scalePts(shape.points, SCALE)
            if (shape.type == "RECT"):
                scaled_pts = rect_to_polygon(scaled_pts)
            draw_shape = plt.Polygon(scaled_pts, closed=True, fill=True,
                                     color=color, edgecolor=color)
            plt.gca().add_patch(draw_shape)


def draw_pin(pin):
    """
    function to draw a PIN object
    :param pin: a pin object
    :return: void
    """
    # chosen color of the PIN in the sketch

    color = "blue"
    pin_name = pin.name.lower()
    if pin_name == "vdd" or pin_name == "gnd":
        color = "blue"
    else:
        color = "red"
    draw_port(pin.info["PORT"], color)

def draw_macro(macro):
    """
    function to draw a Macro (cell) object
    :param macro: a Macro object
    :return: void
    """
    # draw OBS
    draw_obs(macro.info["OBS"], "blue")
    # draw each PIN
    for pin in macro.info["PIN"]:
        draw_pin(pin)

# only draw OBS and PIN
#for each in statements:
#    if each.type == "OBS":
#        draw_obs(each, "blue")
#    elif each.type == "PIN":
#        draw_pin(each)

plt.figure(figsize=(12, 9), dpi=80)
plt.axes()

num_plot = 1
for each in statements:
    if each.type == "MACRO":
        sub = plt.subplot(1, 2, num_plot)
        # need to add title
        sub.set_title(each.name)
        draw_macro(each)
        num_plot += 1
        # scale the axis of the subplot
        plt.axis('scaled')


# start drawing
plt.show()
