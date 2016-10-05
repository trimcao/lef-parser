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
    out_file = (str(corners[0][0]) + '_' + str(corners[0][1]) + '_' +
                str(corners[1][0]) + '_' + str(corners[1][1]))
    plt.savefig(out_folder + out_file)
    # plt.savefig(out_file)
    # plt.show()
    return out_folder + out_file + '.png'


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


def predict_cell(candidates, model, lef_data):
    """
    Use the trained model to choose the most probable cell from via groups.
    :param candidates: 2-via and 3-via groups that could make a cell
    :return: a tuple (chosen via group, predicted cell name)
    """
    margin = 350
    img_width = 200
    img_height = 400
    dataset = np.ndarray(shape=(len(candidates), img_height, img_width),
                              dtype=np.float32)
    for i in range(len(candidates)):
        each_group = candidates[i]
        left_pt = [each_group[0][0][0] - margin, CELL_HEIGHT * 0]
        width = each_group[-1][0][0] - left_pt[0] + margin
        # print (width)
        img_file = plot_window(left_pt, width, CELL_HEIGHT, each_group, lef_data)
        # print (img_file)
        image_data = img_util.load_image(img_file)
        # print (image_data.shape)
        dataset[i, :, :] = image_data

    # print (dataset.shape)
    img_shape = img_width * img_height
    # NOTE: we need to reshape the dataset into the data that ski-learn
    # Logistic Regression uses.
    X_test = dataset.reshape(dataset.shape[0], img_shape)
    result = model.decision_function(X_test)
    print (result)
    scores = []
    predicts = []
    for each_prediction in result:
        scores.append(max(each_prediction))
        predicts.append(np.argmax(each_prediction))
    best_idx = np.argmax(scores)
    return candidates[best_idx], predicts[best_idx]


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
    # print (CELL_HEIGHT)
    print ("Process file:", def_path)
    all_via1 = get_all_vias(def_parser, via_type="M2_M1_via")
    # print (all_via1)

    # sort the vias by row
    via1_sorted = sort_vias_by_row(def_parser.diearea[1], CELL_HEIGHT, all_via1)

    MAX_DISTANCE = 2280 # OR2 cell width, can be changed later
    # via_groups is only one row
    via_groups = group_via(via1_sorted[0], 3, MAX_DISTANCE)
    # print (via_groups[:5])
    # We can load the trained model
    pickle_filename = "logit_model_100316.pickle"
    try:
        with open(pickle_filename, 'rb') as f:
            logit_model = pickle.load(f)
    except Exception as e:
        print('Unable to read data from', pickle_filename, ':', e)

    labels = {0: 'and2', 1: 'inv', 2: 'nand2', 3: 'nor2', 4: 'or2'}
    best_group, prediction = predict_cell(via_groups[1], logit_model, lef_parser)
    print (best_group)
    print (labels[prediction])
    """
    test_group = via_groups[1][0]
    print (test_group)
    left_pt = [test_group[0][0][0] - 350, CELL_HEIGHT * 0]
    width = test_group[-1][0][0] - left_pt[0] + 350
    print (width)
    img_file = plot_window(left_pt, width, CELL_HEIGHT, test_group, lef_parser)
    print (img_file)
    image_data1 = img_util.load_image(img_file)
    print (image_data1.shape)

    test_group = via_groups[1][1]
    print (test_group)
    left_pt = [test_group[0][0][0] - 350, CELL_HEIGHT * 0]
    width = test_group[-1][0][0] - left_pt[0] + 350
    print (width)
    img_file = plot_window(left_pt, width, CELL_HEIGHT, test_group, lef_parser)
    print (img_file)
    image_data2 = img_util.load_image(img_file)
    print (image_data2.shape)

    img_width = 200
    img_height = 400
    test_dataset = np.ndarray(shape=(2, img_height, img_width),
                              dtype=np.float32)

    test_dataset[0, :, :] = image_data1
    test_dataset[1, :, :] = image_data2
    print (test_dataset.shape)
    # LOGISTIC REGRESSION
    img_shape = img_width * img_height

    # NOTE: we need to reshape the dataset into the data that ski-learn Logistic Regression uses.
    X_test = test_dataset.reshape(test_dataset.shape[0], img_shape)

    regr = logit_model

    print (np.argmax(regr.decision_function(X_test[0:1])))
    print (regr.decision_function(X_test[0:1]))


    # Test different functions of Logistic Regression
    my_test = X_test[1:2]
    print (regr.predict(my_test))
    # predict_proba function will output the probability
    print (regr.predict_proba(my_test))
    # decision_function will output the confidence scores
    print (regr.decision_function(my_test))

    my_test = X_test[0:1]
    print (regr.predict(my_test))
    # predict_proba function will output the probability
    print (regr.predict_proba(my_test))
    # decision_function will output the confidence scores
    print (regr.decision_function(my_test))
    """
