"""
Program to extract cell using DEF and LEF data.

Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: October 2016
"""
from def_parser import *
from lef_parser import *
import util
import pickle
import os


def extract_comp(comp_name, lef_data, def_data, macro_via1_dict):
    """
    Extract the features and label of each cell
    :param comp_name: name of the component
    :param lef_data: data parsed from LEF file.
    :param def_data: data parsed from DEF file.
    :param macro_via_dict: dictionary contains macro and via1 data
    :return: void
    """
    # get info of the component and macro from DEF and LEF
    comp_info = def_data.components.comp_dict[comp_name]
    macro_name = comp_info.macro
    macro_info = lef_data.macro_dict[macro_name]
    macro_size = macro_info.info["SIZE"]
    scale = float(def_data.scale)
    # get the placement of the component from DEF file
    bottom_left_pt = comp_info.placed
    top_right_pt = [bottom_left_pt[0] + int(macro_size[0] * scale),
                    bottom_left_pt[1] + int(macro_size[1] * scale)]
    corners = [bottom_left_pt, top_right_pt]
    # find the vias inside the component's area
    vias_in_comp = macro_via1_dict[comp_name]
    vias_draw = []
    for pin in vias_in_comp:
        if pin != "MACRO":
            for each_via in vias_in_comp[pin]:
                each_via_loc = each_via[0]
                via_type = each_via[1]
                if inside_area(each_via_loc, corners):
                    vias_draw.append((each_via_loc, via_type))

    # sort the vias by x-coordinate
    vias_draw.sort(key=lambda x: x[0][0])
    # crop the cell by the vias location
    margin = 350
    left_pt = [vias_draw[0][0][0] - margin, bottom_left_pt[1]]
    width = vias_draw[-1][0][0] - left_pt[0] + margin
    height = macro_size[1] * scale
    corners = [left_pt]
    corners.append([left_pt[0] + width, left_pt[1] + height])

    # build the features
    features = []
    # number of vias
    num_vias = len(vias_draw)
    features.append(num_vias)
    x_bound = left_pt[0]
    y_bound = left_pt[1]
    # NOTE: some cell has 4 vias
    # We suppose maximum vias in a cell is 4
    for each_via in vias_draw:
        x_loc = each_via[0][0] - x_bound
        y_loc = each_via[0][1] - y_bound
        features.append(x_loc)
        features.append(y_loc)
    # if there are only two vias, then there are no via3
    if num_vias < 4:
        temp = [-1 for i in range((4 - num_vias) * 2)]
        features.extend(temp)
    label = macro_name

    return features, label

# Main Class
if __name__ == '__main__':
    lef_file = "./libraries/FreePDK45/gscl45nm.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    train_files = ['c1355.def', "c1355_INVX8.def", "c2670.def", "c2670_no_AND2.def",
                   "c2670_OR2.def", "c3540.def", "c3540_no_AND2.def",
                   "c3540_no_NAND2.def", "c5315.def", "c7552.def"]
    folder = "./libraries/layout_freepdk45/"
    for i in range(len(train_files)):
        def_path = os.path.join(folder, train_files[i])
        print (def_path)
        # def_path = './libraries/layout_freepdk45/c1355.def'
        def_parser = DefParser(def_path)
        def_parser.parse()

        print ("Process file:", def_path)
        # test macro and via (note: only via1)
        macro_via1_dict = util.macro_and_via1(def_parser, via_type="M2_M1_via")
        samples = []
        labels = []
        num_comps = 0
        for each_comp in macro_via1_dict:
            comp_info = def_parser.components.comp_dict[each_comp]
            print (each_comp)
            features, label = extract_comp(each_comp, lef_parser,
                                           def_parser, macro_via1_dict)
            samples.append(features)
            labels.append(label)
            num_comps += 1
            # if num_comps > 10:
            #     break
        # for i in range(len(samples)):
        #     print (samples[i])
        #     print (labels[i])
        #     print ()
        dataset = (samples, labels)
        result_folder = './training_data/'
        set_filename = os.path.join(result_folder, train_files[i])
        set_filename += '.pickle'
        try:
            with open(set_filename, 'wb') as f:
                pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
        print ("Finished!")


