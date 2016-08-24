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

# dictionaries to map the definitions
macro_dict = {}

# can make the stack to be an object if needed
stack = []

# store the statements info in a list
statements = []

# Now try using my data structure to parse
# open the file and start reading
path = "./libraries/FreePDK45/FreePDK45nm.lef"
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
                # add the done statement to a dictionary
                done_obj = stack.pop()
                if isinstance(done_obj, Macro):
                    macro_dict[done_obj.name] = done_obj
                statements.append(done_obj)
        elif nextState == -1:
            pass
        else:
            stack.append(nextState)
            # print (nextState)
f.close()

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
                                color=color)
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
                                     color=color)
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
    # draw OBS (if it exists)
    if "OBS" in macro.info:
        draw_obs(macro.info["OBS"], "blue")
    # draw each PIN
    for pin in macro.info["PIN"]:
        draw_pin(pin)

to_draw = []
to_draw.append(input("Enter the first macro: "))
to_draw.append(input("Enter the second macro: "))
#to_draw = ["AND2X1", "AND2X2"]


plt.figure(figsize=(12, 9), dpi=80)
plt.axes()

num_plot = 1
for macro_name in to_draw:
    # check user's input
    if macro_name not in macro_dict:
        print ("Error: This macro does not exist in the parsed library.")
        quit()
    macro = macro_dict[macro_name]
    sub = plt.subplot(1, 2, num_plot)
    # need to add title
    sub.set_title(macro.name)
    draw_macro(macro)
    num_plot += 1
    # scale the axis of the subplot
    plt.axis('scaled')


# start drawing
print ("Start drawing...")
plt.show()

#print (macro_dict)
#print (len(macro_dict))

