"""
Program to plot vias in the whole layout using DEF and LEF data.

Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: September 2016
"""

from def_parser import *
from lef_parser import *
from util import *
import plot_cell
import matplotlib.pyplot as plt
import time

def get_all_vias(def_info, via_type):
    """
    method to get all vias of the via_type and put them in a list
    :param def_info: DEF data
    :param via_type: via type
    :return: a list of all vias
    """
    vias = []
    # process the nets
    for net in def_info.nets.nets:
        for route in net.routed:
            if route.end_via != None:
                # check for the via type of the end_via
                if route.end_via[:len(via_type)] == via_type:
                    via_loc = route.end_via_loc
                    via_name = route.end_via
                    via_info = (via_loc, via_name)
                    # add a via to the vias list
                    vias.append(via_info)
    #print (result_dict)
    return vias

def sort_vias_by_row(layout_area, row_height, vias):
    """
    Sort the vias by row
    :param layout_area: a list [x, y] that stores the area of the layout
    :param vias: a list of vias that need to be sorted
    :return: a list of rows, each containing a list of vias in that row.
    """
    num_rows = layout_area[1] // row_height + 1
    rows = []
    for i in range(num_rows):
        rows.append([])
    for via in vias:
        via_y = via[0][1]
        row_dest = via_y // row_height
        rows[row_dest].append(via)
    # sort vias in each row based on x-coordinate
    for each_row in rows:
        each_row.sort(key = lambda x: x[0][0])
    return rows

def plot_window(left_pt, width, height, vias, lef_data):
    """
    Method to plot a window from the layout with all vias inside it.
    :param left_pt: bottom left point (origin) of the window
    :param width: width of the window
    :param height: height of the window
    :param vias: a list containing all vias on a row
    :return: void
    """
    plt.figure(figsize=(7, 5), dpi=80, frameon=False)
    # get the corners for the window
    corners = [left_pt]
    # corners.append((left_pt[0] + width, left_pt[1]))
    corners.append((left_pt[0] + width, left_pt[1] + height))
    # corners.append((left_pt[0], left_pt[1] + height))
    print (corners)
    # scale the axis of the subplot
    # axis = [corners[0][0], corners[1][0], corners[0][1], corners[1][1]]
    # plt.axis(axis)
    # draw the window boundary
    scaled_pts = rect_to_polygon(corners)
    draw_shape = plt.Polygon(scaled_pts, closed=True, fill=None,
                             color="blue")
    plt.gca().add_patch(draw_shape)

    # plot the vias inside the windows
    # look for the vias
    for via in vias:
        if (via[0][0] > width):
            break
        via_name = via[1]
        via_info = lef_data.via_dict[via_name]
        via_loc = via[0]
        plot_cell.draw_via(via_loc, via_info)

    # plt.gca().set_aspect('equal', adjustable='box')
    plt.axis('scaled')
    plt.show()

def group_via(via_list, max_number, max_distance):
    """
    Method to group the vias together to check if they belong to a cell.
    :param via_list: a list of all vias.
    :return: a list of groups of vias.
    """
    groups = []
    length = len(via_list)
    for i in range(length):
        # one_group = [via_list[i]]
        curr_via = via_list[i]
        for j in range(2, max_number + 1):
            if i + j - 1 < length:
                right_via = via_list[i + j - 1]
                dist = right_via[0][0] - curr_via[0][0]
                if dist < max_distance:
                    groups.append(via_list[i:i+j])
    return groups



# Main Class
if __name__ == '__main__':
    def_path = './libraries/layout_freepdk45/c880.def'
    def_parser = DefParser(def_path)
    def_parser.parse()
    scale = def_parser.scale

    lef_file = "./libraries/FreePDK45/gscl45nm.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    CELL_HEIGHT = int(float(scale) * lef_parser.cell_height)
    print (CELL_HEIGHT)

    print ("Process file:", def_path)
    all_via1 = get_all_vias(def_parser, via_type="M2_M1_via")
    # print (all_via1)
    # print (len(all_via1))

    # sort the vias by row
    via1_sorted = sort_vias_by_row(def_parser.diearea[1], cell_height, all_via1)

    # for each_row in via1_sorted:
    #     print (each_row)

    # just try to plot an arbitrary window
    # plot_window((0, 0), 15000, cell_height, via1_sorted[0], lef_parser)

    MAX_DISTANCE = 2280 # OR2 cell width, can be changed later
    via_groups = group_via(via1_sorted[0], 3, MAX_DISTANCE)
    print (via_groups[:10])
    # print (via1_sorted[0][:10])
