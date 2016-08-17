"""
Useful functions
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

def str_to_list(s):
    """
    Function to turn a string separated by space into list of words
    :param s: input string
    :return: a list of words
    """
    result = s.split()
    # check if the last word is ';' and remove it
    if len(result) >= 1:
        if result[len(result) - 1] == ";":
            result.pop()
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


def split_parentheses(info):
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






