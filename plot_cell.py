"""
Program to plot cell using DEF and LEF data.

Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: September 2016
"""
from def_parser import *
from lef_parser import *
import matplotlib.pyplot as plt

def inside_area(location, corners):
    """
    Check if the location is inside an area.
    :param location: location
    :param corners: corner points of the rectangle area.
    :return:
    """
    x1 = corners[0][0]
    x2 = corners[1][0]
    y1 = corners[0][1]
    y2 = corners[1][1]
    return (location[0] > x1 and location[0] < x2
            and location[1] > y1 and location[1] < y2)


def macro_and_via1(def_info):
    """
    Method to get macros/cells info and via1 information.
    :param def_info: information from a DEF file
    :return: a macro dictionary that contains via info
    """
    result_dict = {}
    # add components to the dictionary
    for each_comp in def_info.components.comps:
        result_dict[each_comp.name] = {}
        result_dict[each_comp.name]["MACRO"] = each_comp.macro
    # process the nets
    for net in def_info.nets.nets:
        for route in net.routed:
            if route.end_via != None:
                if route.end_via[:4] == "via1":
                    via_loc = route.end_via_loc
                    # add the via to the component dict
                    for each_comp in net.comp_pin:
                        comp_name = each_comp[0]
                        pin_name = each_comp[1]
                        if comp_name in result_dict:
                            if pin_name in result_dict[comp_name]:
                                result_dict[comp_name][pin_name].append(via_loc)
                            else:
                                result_dict[comp_name][pin_name] = [via_loc]
    #print (result_dict)
    return result_dict

def draw_via(location, via_info, color='blue'):
    """
    Method to draw a via using the location and VIA info from the LEF file.
    :param location: via location
    :param via_info: VIA data from LEF file.
    :return: void
    """
    for each_layer in via_info.layers:
        # print (each_layer.name)
        if each_layer.name == 'metal2':
            color = 'red'
        for shape in each_layer.shapes:
            scaled_pts = scalePts(shape.points, SCALE)
            for i in range(len(scaled_pts)):
                scaled_pts[i][0] += location[0]
                scaled_pts[i][1] += location[1]
            # print (scaled_pts)
            if shape.type == "RECT":
                scaled_pts = rect_to_polygon(scaled_pts)
            # print (scaled_pts)
            draw_shape = plt.Polygon(scaled_pts, closed=True, fill=True,
                                     color=color)
            plt.gca().add_patch(draw_shape)

# Main Class
if __name__ == '__main__':
    read_path = './libraries/DEF/c1908_tri_no_metal1.def'
    def_parser = DefParser(read_path)
    def_parser.parse()
    scale = float(def_parser.scale)

    lef_file = "./libraries/Nangate/NangateOpenCellLibrary.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()
    # test macro and via (note: only via1)
    macro_via1_dict = macro_and_via1(def_parser)
    # for comp in macro_dict:
    #     print (comp)
    #     for pin in macro_dict[comp]:
    #         print ("    " + pin + ": " + str(macro_dict[comp][pin]))
    #     print ()


    # try to get the boundary of U825
    u825 = def_parser.components.comp_dict["U669"]
    # print (u825)
    # so we get the placement of U825
    # now we get the size info of NAND2_X1
    # nand2 = lef_parser.macro_dict["NAND2_X1"]
    nand2 = lef_parser.macro_dict["AND2_X1"]
    # print (nand2)
    nand2_size = nand2.info["SIZE"]
    # print (scale)
    # show four points of the rectangle of U825
    pt1 = u825.placed
    pt2 = [int(u825.placed[0] + nand2_size[0] * scale),
           int(u825.placed[1] + nand2_size[1] * scale)]
    pt2[0] -= pt1[0]
    pt2[1] -= pt1[1]
    # print (pt1)
    # print (pt2)
    corners = [[0, 0], pt2]

    # study U825
    # u825_via1 = macro_via1_dict["U825"]
    u825_via1 = macro_via1_dict["U669"]
    vias = []
    for pin in u825_via1:
        print ("    " + pin + ": ")
        for each_via in u825_via1[pin]:
            if pin != "MACRO":
                new_via = [each_via[0], each_via[1]]
                new_via[0] = each_via[0] - pt1[0]
                new_via[1] = each_via[1] - pt1[1]
                if inside_area(new_via, corners):
                    print (new_via)
                    vias.append(new_via)
        print ()

    # just plot U825
    # NOTE: figsize(6, 9) can be changed to adapt to other cell size
    plt.figure(figsize=(6, 9), dpi=80, frameon=False)
    # plt.figure()
    # fig = plt.figure(frameon=False)
    # fig.set_size_inches(5, 8)
    # ax = plt.Axes(fig, [0., 0., 1., 1.], )
    # ax.set_axis_off()
    # fig.add_axes(ax)
    #plt.axes()
    scaled_pts = rect_to_polygon(corners)
    # print (scaled_pts)
    draw_shape = plt.Polygon(scaled_pts, closed=True, fill=None,
                             color="blue")
    plt.gca().add_patch(draw_shape)
    # add some vias
    # NOTE: via1 has many variations, later need to save those variations
    via1_info = lef_parser.via_dict["via1_4"]
    via1_info = lef_parser.via_dict["via1_1"]
    for via in vias:
        draw_via(via, via1_info)
    # scale the axis of the subplot
    test_axis = [corners[0][0], corners[1][0], corners[0][1], corners[1][1]]
    # print (test_axis)
    plt.axis(test_axis)
    # plt.axis('scaled')
    plt.axis('off')
    #plt.axis('equal')
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.savefig('foo.png', bbox_inches='tight')
    plt.savefig('./images/and.png')
    plt.show()
