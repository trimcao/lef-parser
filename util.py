"""
Useful functions
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

SCALE = 2000
import matplotlib.pyplot as plt

def str_to_list(s):
    """
    Function to turn a string separated by space into list of words
    :param s: input string
    :return: a list of words
    """
    result = s.split()
    # check if the last word is ';' and remove it
    #if len(result) >= 1:
    #    if result[len(result) - 1] == ";":
    #        result.pop()
    return result

def scalePts(pts, alpha):
    """
    scale a list of points
    :return:
    """
    scaled = []
    for pt in pts:
        scaled_pt = (alpha*pt[0], alpha*pt[1])
        scaled.append(scaled_pt)
    return scaled

def rect_to_polygon(rect_pts):
    """
    Convert the rect point list into polygon point list (for easy plotting)
    :param pts:
    :return:
    """
    poly_pt = []
    pt1 = list(rect_pts[0])
    poly_pt.append(pt1)
    pt2 = [rect_pts[0][0], rect_pts[1][1]]
    poly_pt.append(pt2)
    pt3 = list(rect_pts[1])
    poly_pt.append(pt3)
    pt4 = [rect_pts[1][0], rect_pts[0][1]]
    poly_pt.append(pt4)
    return poly_pt


def split_parentheses(info: object) -> object:
    """
    make all strings inside parentheses a list
    :param s: a list of strings (called info)
    :return: info list without parentheses
    """
    # if we see the "(" sign, then we start adding stuff to a temp list
    # in case of ")" sign, we append the temp list to the new_info list
    # otherwise, just add the string to the new_info list
    new_info = []
    make_list = False
    current_list = []
    for idx in range(len(info)):
        if info[idx] == "(":
            make_list = True
        elif info[idx] == ")":
            make_list = False
            new_info.append(current_list)
            current_list = []
        else:
            if make_list:
                current_list.append(info[idx])
            else:
                new_info.append(info[idx])
    return new_info


def split_plus(line):
    """
    Split a line according to the + (plus) sign.
    :param line:
    :return:
    """
    new_line = line.split("+")
    return new_line

def split_space(line):
    """
    Split a line according to space.
    :param line:
    :return:
    """
    new_line = line.split()
    return new_line


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

def compare_metal(metal_a, metal_b):
    """
    Compare metal layers
    :param metal_a: the first metal layer description
    :param metal_b: the second metal layer description
    :return:
    """
    if metal_a == "poly":
        if metal_b == "poly":
            return 0
        else:
            return -1
    else:
        if metal_b == "poly":
            return 1
        else:
            metal_a_num = get_metal_num(metal_a)
            metal_b_num = get_metal_num(metal_b)
            return (metal_a_num - metal_b_num)


def get_metal_num(metal):
    """
    Get mental layer number from a string, such as "metal1" or "metal10"
    :param metal: string that describes the metal layer
    :return: metal number
    """
    len_metal = len("metal")
    parse_num = ""
    for idx in range(len_metal, len(metal)):
        parse_num += metal[idx]
    return int(parse_num)