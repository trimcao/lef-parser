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
import numpy as np
import time
import img_util
from sklearn.linear_model import LogisticRegression
# from six.moves import cPickle as pickle
import pickle
import random

def get_all_vias(def_info, via_type):
    """
    method to get all vias of the via_type and put them in a list
    :param def_info: DEF data
    :param via_type: via type
    :return: a list of all vias
    """
    vias = []
    net_to_via = {}
    # process the nets
    num_vias = 0
    for net in def_info.nets.nets:
        net_to_via[net.name] = []
        for route in net.routed:
            if route.end_via != None:
                # check for the via type of the end_via
                if route.end_via[:len(via_type)] == via_type:
                    via_loc = route.end_via_loc
                    via_name = route.end_via
                    via_info = (via_loc, via_name, num_vias, net.name)
                    # add a via to the vias list
                    vias.append(via_info)
                    # net_to_via dict will point to via index
                    net_to_via[net.name].append(num_vias)
                    num_vias += 1
    #print (result_dict)
    return vias, net_to_via

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


def plot_window(left_pt, width, height, vias, lef_data, macro=None, comp=None):
    """
    Method to plot a window from the layout with all vias inside it.
    :param left_pt: bottom left point (origin) of the window
    :param width: width of the window
    :param height: height of the window
    :param vias: a list containing all vias on a row
    :return: void
    """
    plt.figure(figsize=(3, 5), dpi=80, frameon=False)
    # get the corners for the window
    corners = [left_pt]
    corners.append((left_pt[0] + width, left_pt[1] + height))
    # scale the axis of the subplot
    # draw the window boundary
    # scaled_pts = rect_to_polygon(corners)
    # draw_shape = plt.Polygon(scaled_pts, closed=True, fill=None,
    #                          color="blue")
    # plt.gca().add_patch(draw_shape)

    # plot the vias inside the windows
    # look for the vias
    for via in vias:
        if (via[0][0] - left_pt[0] > width):
            break
        via_name = via[1]
        via_info = lef_data.via_dict[via_name]
        via_loc = via[0]
        plot_cell.draw_via(via_loc, via_info)

    # scale the axis of the subplot
    axis = [corners[0][0], corners[1][0], corners[0][1], corners[1][1]]
    # print (test_axis)
    plt.axis(axis)
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    # compose the output file name
    out_folder = './images/'
    # current_time = time.strftime('%H%M%d%m%Y')
    pos = (str(corners[0][0]) + '_' + str(corners[0][1]) + '_' +
                str(corners[1][0]) + '_' + str(corners[1][1]))
    # out_file = out_folder + pos
    out_file = out_folder
    # out_file += str(corners[0][0])
    out_file += pos
    if macro:
        out_file += '_' + macro
    if comp:
        out_file += '_' + comp
    current_time = time.strftime('%H%M%S%d%m%Y')
    out_file += '_' + current_time
    # plt.savefig(out_file, transparent=True)
    plt.savefig(out_file)
    # plt.show()
    plt.close('all')
    return out_file + '.png'


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
        curr_list = []
        for j in range(2, max_number + 1):
            if i + j - 1 < length:
                right_via = via_list[i + j - 1]
                dist = right_via[0][0] - curr_via[0][0]
                if dist < max_distance:
                    curr_list.append(via_list[i:i+j])
        # only add via group list that is not empty
        if len(curr_list) > 0:
            groups.append(curr_list)
    return groups


def predict_cell(candidates, row, model, lef_data, std_cells):
    """
    Use the trained model to choose the most probable cell from via groups.
    :param candidates: 2-via and 3-via groups that could make a cell
    :return: a tuple (chosen via group, predicted cell name)
    """
    margin = 350
    img_width = 200
    img_height = 400
    img_shape = img_width * img_height
    possible_candidates = []
    for i in range(len(candidates)):
        # dataset = np.ndarray(shape=(len(candidates), img_height, img_width),
        #                      dtype=np.float32)
        if candidates[i] != -1:
            possible_candidates.append(i)
            dataset = np.ndarray(shape=(1, img_height, img_width),
                                 dtype=np.float32)
            each_group = candidates[i]
            left_pt = [each_group[0][0][0] - margin, CELL_HEIGHT * row]
            width = each_group[-1][0][0] - left_pt[0] + margin
            # print (width)
            img_file = plot_window(left_pt, width, CELL_HEIGHT, each_group, lef_data)
            # print (img_file)
            image_data = img_util.load_image(img_file)
            # print (image_data.shape)
            dataset[0, :, :] = image_data
            X_test = dataset.reshape(dataset.shape[0], img_shape)
            result = model.decision_function(X_test)
            result = result[0]
            # print (result)
            # check for result
            if result[i] == max(result):
                return candidates[i], i
    # if we cannot find a solution, randomly select a choice
    choice = random.choice(possible_candidates)
    return candidates[choice], choice


def sorted_components(layout_area, row_height, comps):
    """
    Sort the components by row
    :param layout_area: a list [x, y] that stores the area of the layout
    :param comps: a list of components that need to be sorted
    :return: a list of rows, each containing a list of components in that row.
    """
    num_rows = layout_area[1] // row_height + 1
    rows = []
    for i in range(num_rows):
        rows.append([])
    for comp in comps:
        comp_y = comp.placed[1]
        row_dest = comp_y // row_height
        rows[row_dest].append(comp)
    # sort vias in each row based on x-coordinate
    for each_row in rows:
        each_row.sort(key = lambda x: x.placed[0])
    return rows


def predict_row():
    # We can load the trained model
    pickle_filename = "./trained_models/logit_model_100916_2.pickle"
    try:
        with open(pickle_filename, 'rb') as f:
            logit_model = pickle.load(f)
    except Exception as e:
        print('Unable to read data from', pickle_filename, ':', e)

    labels = {0: 'and2', 1: 'invx1', 2: 'invx8', 3: 'nand2', 4: 'nor2',
              5: 'or2'}
    cell_labels = {'AND2X1': 'and2', 'INVX1': 'invx1', 'NAND2X1': 'nand2',
                   'NOR2X1': 'nor2', 'OR2X1': 'or2', 'INVX8': 'invx8'}

    # process
    # print the sorted components
    components = sorted_components(def_parser.diearea[1], CELL_HEIGHT,
                                   def_parser.components.comps)
    correct = 0
    total_cells = 0
    predicts = []
    actuals = []
    # via_groups is only one row
    # for i in range(len(via1_sorted)):
    for i in range(3, 4):
        via_groups = group_via(via1_sorted[i], 3, MAX_DISTANCE)
        visited_vias = [] # later, make visited_vias a set to run faster
        cells_pred = []
        for each_via_group in via_groups:
            first_via = each_via_group[0][0]
            # print (first_via)
            if not first_via in visited_vias:
                best_group, prediction = predict_cell(each_via_group, i,
                                                      logit_model, lef_parser)
                # print (best_group)
                # print (labels[prediction])
                cells_pred.append(labels[prediction])
                for each_via in best_group:
                    visited_vias.append(each_via)
                    # print (best_group)
                    # print (labels[prediction])

        print (cells_pred)
        print (len(cells_pred))

        actual_comp = []
        actual_macro = []
        for each_comp in components[i]:
            actual_comp.append(cell_labels[each_comp.macro])
            actual_macro.append(each_comp.macro)
        print (actual_comp)
        print (len(actual_comp))

        # check predictions vs actual cells
        # for i in range(len(actual_comp)):
        #     if cells_pred[i] == actual_comp[i]:
        #         correct += 1
        num_correct, num_cells = predict_score(cells_pred, actual_comp)

        correct += num_correct
        total_cells += num_cells
        predicts.append(cells_pred)
        actuals.append(actual_comp)

        print ()

    print (correct)
    print (total_cells)
    print (correct / total_cells * 100)


def predict_score(predicts, actuals):
    """
    Find the number of correct cell predictions.
    :param predicts: a list of predictions.
    :param actuals: a list of actual cells.
    :return: # correct predictions, # cells
    """
    len_preds = len(predicts)
    len_actuals = len(actuals)
    shorter_len = min(len_preds, len_actuals)
    gap_predict = 0
    gap_actual = 0
    num_correct = 0
    # print (shorter_len)
    for i in range(shorter_len):
        # print (i)
        # print (gap_predict)
        # print (gap_actual)
        # print ()
        if predicts[i + gap_predict] == actuals[i + gap_actual]:
            num_correct += 1
        else:
            if len_preds < len_actuals:
                gap_actual += 1
                len_preds += 1
            elif len_preds > len_actuals:
                gap_predict += 1
                len_actuals += 1
    return num_correct, len(actuals)


def plot_cell_w_vias():
    # process each row, plot all cells
    # for i in range(num_rows):
    margin = 350
    for i in range(1):
        via_idx = 0
        print (len(components[i]))
        print (len(via1_sorted[i]))
        for each_comp in components[i]:
            comp_name = each_comp.name
            macro_name = each_comp.macro
            macro_data = lef_parser.macro_dict[macro_name]
            num_vias = len(macro_data.pin_dict) - 2 # because of VDD and GND pins
            # get the vias
            cell_vias = via1_sorted[i][via_idx:via_idx + num_vias]
            # update via_idx
            via_idx += num_vias
            # plot the cell
            left_pt = [cell_vias[0][0][0] - margin, CELL_HEIGHT * i]
            width = cell_vias[-1][0][0] - left_pt[0] + margin
            # print (width)
            img_file = plot_window(left_pt, width, CELL_HEIGHT, cell_vias,
                                   lef_parser, macro=macro_name, comp = comp_name)
            print (comp_name)
            print (macro_name)
            print (cell_vias)
            print (via_idx)
    print('Finished!')

def check_via_group(via_group, source_sink):
    """
    Check the validity of each via set in the via group.
    :param via_group: the via_group in question.
    :return: via_group with all valid candidate(s)
    """
    # valid for 2-via cell: 1 source, 1 sink
    # valid for 3-via cell: 2 sink, 1 source
    valid_group = []
    for each_group in via_group:
        num_vias = len(each_group)
        num_source = 0
        num_sink = 0
        for each_via in each_group:
            # 0 = sink, 1 = source
            if source_sink[each_via[2]] == 1:
                num_source += 1
            elif source_sink[each_via[2]] == 0:
                num_sink += 1
        if num_source <= 1 and num_sink <=2:
            valid_group.append(each_group)
    return valid_group


def get_candidates(first_via_idx, via_list, std_cells):
    """
    Generate a list of candidates from the first via.
    Each standard cell will be considered for candidates.
    If the standard cell cannot be placed there, the value is -1,
     otherwise, it will be a list of vias.
    :param first_via_idx: first via index in the via_list
    :param via_list: the list of all vias (in a row)
    :param std_cells: a list that stores information of std cells
    :return: a list of groups of vias, or -1
    """
    # candidates = [-1 for i in range(len(std_cells))]
    candidates = []
    first_via = via_list[first_via_idx]
    # print (first_via)
    first_via_x = first_via[0][0]
    for i in range(len(std_cells)):
        cell_width = std_cells[i][2]
        min_vias = std_cell_info[i][0]
        max_vias = std_cells[i][1]
        pin_left_dist = std_cells[i][3]
        boundary = first_via_x + cell_width - pin_left_dist
        # possible vias contain the vias inside the boundary
        possible_vias = [first_via]
        for j in range(first_via_idx + 1, len(via_list)):
            if via_list[j][0][0] <= boundary:
                possible_vias.append(via_list[j])
            else:
                break
        # check the candidate against cell info
        if len(possible_vias) > max_vias or len(possible_vias) < min_vias:
            candidates.append(-1)
        else:
            candidates.append(possible_vias)
    return candidates




# Main Class
if __name__ == '__main__':
    def_path = './libraries/layout_freepdk45/c1908.def'
    def_parser = DefParser(def_path)
    def_parser.parse()
    scale = def_parser.scale

    lef_file = "./libraries/FreePDK45/gscl45nm.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    CELL_HEIGHT = int(float(scale) * lef_parser.cell_height)
    # print (CELL_HEIGHT)
    print ("Process file:", def_path)
    all_via1, net_to_via = get_all_vias(def_parser, via_type="M2_M1_via")
    # print (all_via1)

    # sort the vias by row
    via1_sorted = sort_vias_by_row(def_parser.diearea[1], CELL_HEIGHT, all_via1)

    MAX_DISTANCE = 2280 # OR2 cell width, can be changed later

    components = sorted_components(def_parser.diearea[1], CELL_HEIGHT,
                                   def_parser.components.comps)

    num_rows = len(components)

    # source/sink list for vias
    # -1 = don't know, 0 = sink, 1 = source
    # source_sink = [-1 for i in range(len(all_via1))]
    # print (net_to_via['n192'])
    #
    # # inputs and outputs of the c432 design
    # inputs = 'N1, N4, N8, N11, N14, N17, N21, N24, N27, N30, N34, N37, N40, N43, N47, '
    # inputs += 'N50, N53, N56, N60, N63, N66, N69, N73, N76, N79, N82, N86, N89, N92, '
    # inputs += 'N95, N99, N102, N105, N108, N112, N115'
    # outputs = 'N223, N329, N370, N421, N430, N431, N432'
    #
    # inputs = inputs.split(', ')
    # outputs = outputs.split(', ')
    #
    # # assign source/sink to inputs and outputs
    # for each_in in inputs:
    #     for each_via in net_to_via[each_in]:
    #         source_sink[each_via] = 0
    # for each_out in outputs:
    #     for each_via in net_to_via[each_out]:
    #         source_sink[each_via] = 1

    ####
    # test remove the redundant via in row 4th of c432
    # we cannot check redundant vias via adjacent vias
    # maybe I do not implement this correctly
    # probably this is not a good idea

    # row4 = via1_sorted[3]
    # print ("length of row4 before: ", len(row4))
    # row4_new = []
    # for i in range(1, len(row4)):
    #     if row4[i][3] != row4[i - 1][3]:
    #         row4_new.append(row4[i - 1])
    # row4_new.append(row4[-1])
    # print ("length of row4 after: ", len(row4_new))
    #
    # via1_sorted[3] = row4_new


    ###############
    # DO PREDICTION
    # predict_row()
    # We can load the trained model
    pickle_filename = "./trained_models/logit_model_100916_2.pickle"
    try:
        with open(pickle_filename, 'rb') as f:
            logit_model = pickle.load(f)
    except Exception as e:
        print('Unable to read data from', pickle_filename, ':', e)

    labels = {0: 'and2', 1: 'invx1', 2: 'invx8', 3: 'nand2', 4: 'nor2',
              5: 'or2'}
    cell_labels = {'AND2X1': 'and2', 'INVX1': 'invx1', 'NAND2X1': 'nand2',
                   'NOR2X1': 'nor2', 'OR2X1': 'or2', 'INVX8': 'invx8'}

    ##############
    # List of standard cells
    std_cell_info = {}
    # info includes (min num vias, max num vias, width,
    #  distance from left boundary to first pin)
    # I wonder if max num vias should be used, actually I don't know what is the
    # maximum number of vias, but I guess +1 is fine.
    # 0 is and2, 1 is invx1, etc.
    std_cell_info[0] = (3, 4, 2280, 295)
    std_cell_info[1] = (2, 3, 1140, 315)
    std_cell_info[2] = (2, 3, 2660, 695)
    std_cell_info[3] = (3, 4, 1520, 90)
    std_cell_info[4] = (3, 4, 1520, 315)
    std_cell_info[5] = (3, 4, 2280, 695)

    # process
    # print the sorted components
    components = sorted_components(def_parser.diearea[1], CELL_HEIGHT,
                                   def_parser.components.comps)
    correct = 0
    total_cells = 0
    predicts = []
    actuals = []
    # via_groups is only one row
    for i in range(len(via1_sorted)):
    # for i in range(4, 5):
        print ('Process row', (i + 1))
        # each via group in via_groups consist of two candidates
        # via_groups = group_via(via1_sorted[i], 3, MAX_DISTANCE)
        visited_vias = [] # later, make visited_vias a set to run faster
        cells_pred = []
        via_idx = 0
        while via_idx < len(via1_sorted[i]):
            # choosing candidates
            candidates = get_candidates(via_idx, via1_sorted[i], std_cell_info)
            best_group, prediction = predict_cell(candidates, i, logit_model,
                                                  lef_parser, std_cell_info)
            via_idx += len(best_group)
            # print (best_group)
            # print (labels[prediction])
            cells_pred.append(labels[prediction])
            for each_via in best_group:
                visited_vias.append(each_via)

        # for each_via_group in via_groups:
            # check source/sink validity for each candidate in the via_group
            # valid_via_group = check_via_group(each_via_group, source_sink)

            # first_via = each_via_group[0][0]
            # print (first_via)
            # if not first_via in visited_vias:
            #     best_group, prediction = predict_cell(each_via_group, i,
            #                                           logit_model, lef_parser)
            #     print (best_group)
            #     print (labels[prediction])
            #     cells_pred.append(labels[prediction])
            #     for each_via in best_group:
            #         visited_vias.append(each_via)
            #     # add source/sink to via
            #     # if we have a source, then all other vias with the same net are sink
            #     for each_via in best_group[:-1]:
            #         via_id = each_via[2]
            #         if source_sink[via_id] == -1:
            #             source_sink[each_via[2]] = 0
            #     # assign the output a source node
            #     last_via = best_group[-1]
            #     last_via_id = last_via[2]
            #     if source_sink[via_id] == -1:
            #         source_sink[each_via[2]] = 1
            #     # update other nodes in the same net as sink
            #     source_net = last_via[3]
            #     vias_in_source_net = net_to_via[source_net]
            #     for via_id in vias_in_source_net:
            #         if via_id != last_via_id:
            #             source_sink[via_id] = 0

        print (cells_pred)
        print (len(cells_pred))

        actual_comp = []
        actual_macro = []
        for each_comp in components[i]:
            actual_comp.append(cell_labels[each_comp.macro])
            actual_macro.append(each_comp.macro)
        print (actual_comp)
        print (len(actual_comp))

        # check predictions vs actual cells
        # for i in range(len(actual_comp)):
        #     if cells_pred[i] == actual_comp[i]:
        #         correct += 1
        num_correct, num_cells = predict_score(cells_pred, actual_comp)

        correct += num_correct
        total_cells += num_cells
        predicts.append(cells_pred)
        actuals.append(actual_comp)

        print ()

    print (correct)
    print (total_cells)
    print (correct / total_cells * 100)
