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



