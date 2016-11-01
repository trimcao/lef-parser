"""
Train a ML model to predict cells based on vias location

Name: Tri Minh Cao
Email: tricao@utdallas.edu
Date: October 2016
"""

import pickle
import random
import os
from def_parser import *
from lef_parser import *
import util
from sklearn.linear_model import LogisticRegression
import numpy as np
import plot_layout

# idea: get 900 cells from each type
# separate all data into bins labeled by macro name (AND2, INVX1, etc.)
# when I train, I will select randomly samples from those bins
FEATURE_LEN = 9


def save_data_pickle(dataset, filename):
    # pickle the merged data
    filename = "./merged_data/freepdk45_10_17_16.pickle"
    try:
        with open(filename, 'wb') as f:
            pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', set_filename, ':', e)


def merge_data(data_folder, num_cells):
    """
    Read from data pickle files, and merge
    :return:
    """
    random.seed(12345)

    all_samples = []
    all_labels = []

    pickle_folder = "./training_data"
    pickle_files = os.listdir(data_folder)
    for file in pickle_files:
        pickle_file = os.path.join(data_folder, file)
        try:
            with open(data_folder, 'rb') as f:
                dataset = pickle.load(f)
        except Exception as e:
            print('Unable to read data from', pickle_file, ':', e)
        all_samples.extend(dataset[0])
        all_labels.extend(dataset[1])

    all_dataset = (all_samples, all_labels)

    dataset = {}
    dataset['AND2X1'] = []
    dataset['INVX1'] = []
    dataset['INVX8'] = []
    dataset['NAND2X1'] = []
    dataset['NOR2X1'] = []
    dataset['OR2X1'] = []

    choices = [i for i in range(len(all_samples))]
    random.shuffle(choices)
    for idx in choices:
        features = all_samples[idx]
        label = all_labels[idx]
        if len(dataset[label]) < num_cells:
            dataset[label].append(features)
        cont = False
        for each_macro in dataset:
            if len(dataset[each_macro]) < num_cells:
                cont = True
        if not cont:
            break

    for each_macro in dataset:
        print (each_macro)
        print (len(dataset[each_macro]))

    # pickle the selected data
    set_filename = "./merged_data/selected_10_17_16.pickle"
    save_data_pickle(dataset, set_filename)

    # should return the merged data set
    return dataset


def train_model(dataset, train_len):
    """
    Method to train model
    :param dataset: dataset
    :param train_len: total length of training set
    :return: trained model
    """

    train_dataset = np.ndarray(shape=(train_len, FEATURE_LEN),
                               dtype=np.int32)
    train_label = np.ndarray(train_len,
                             dtype=np.int32)
    current_size = 0
    num_selected = [0, 0, 0, 0, 0, 0]
    while current_size < train_len:
        choice = random.randrange(6) # we have 6 types of cells
        cur_label = num_to_label[choice]
        cur_idx = num_selected[choice]
        train_dataset[current_size, :] = np.array(dataset[cur_label][cur_idx],
                                                  dtype=np.int32)
        train_label[current_size] = choice
        current_size += 1
        num_selected[choice] += 1

    # shuffle the dataset
    train_dataset, train_label = util.randomize(train_dataset, train_label)

    test_dataset = train_dataset[4500:] # why 4500 here?
    test_label = train_label[4500:]
    train_dataset = train_dataset[:4500]
    train_label = train_label[:4500]

    # train a logistic regression model
    regr = LogisticRegression()
    X_train = train_dataset
    y_train = train_label

    X_test = test_dataset
    y_test = test_label

    regr.fit(X_train, y_train)
    score = regr.score(X_test, y_test)
    pred_labels = regr.predict(X_test)
    print(pred_labels[:100])
    print(score)

    # Save the trained model for later use
    filename = "./trained_models/logit_model_103116.pickle"
    save_data_pickle(regr, filename)
    # return the trained model
    return regr


def predict_cell(candidates, row, model, lef_data):
    """
    Use the trained model to choose the most probable cell from via groups.
    :param candidates: 2-via and 3-via groups that could make a cell
    :return: a tuple (chosen via group, predicted cell name)
    """
    # FIXME: re-write this method, remove the margin
    # possibly I can use the current method of testing the width of each cell
    margin = 350
    dataset = np.ndarray(shape=(len(candidates), FEATURE_LEN),
                         dtype=np.float32)
    for i in range(len(candidates)):
        features = []
        each_group = candidates[i]
        left_pt = [each_group[0][0][0] - margin, CELL_HEIGHT * row]
        width = each_group[-1][0][0] - left_pt[0] + margin
        num_vias = len(each_group)
        features.append(num_vias)
        x_bound = left_pt[0]
        y_bound = left_pt[1]
        # NOTE: some cell has 4 vias
        # We suppose maximum vias in a cell is 4
        for each_via in each_group:
            x_loc = each_via[0][0] - x_bound
            y_loc = each_via[0][1] - y_bound
            features.append(x_loc)
            features.append(y_loc)
        # if there are only two vias, then there are no via3
        if num_vias < 4:
            temp = [-1 for i in range((4 - num_vias) * 2)]
            features.extend(temp)
        dataset[i, :] = np.array(features, dtype=np.int32)

    # Logistic Regression uses.
    X_test = dataset
    # print (X_test)

    result = model.decision_function(X_test)
    proba = model.predict_proba(X_test)
    # print (result)
    scores = []
    predicts = []
    for each_prediction in result:
        scores.append(max(each_prediction))
        predicts.append(np.argmax(each_prediction))
    best_idx = np.argmax(scores)
    return candidates[best_idx], predicts[best_idx]


def predict_row():
    # FIXME: restructure this method
    # We can load the trained model
    pickle_filename = "./trained_models/logit_model_101716.pickle"
    logit_model = load_data_pickle(pickle_filename)

    labels = {0: 'and2', 1: 'invx1', 2: 'invx8', 3: 'nand2', 4: 'nor2',
              5: 'or2'}
    cell_labels = {'AND2X1': 'and2', 'INVX1': 'invx1', 'NAND2X1': 'nand2',
                   'NOR2X1': 'nor2', 'OR2X1': 'or2', 'INVX8': 'invx8'}

    # process
    components = util.sorted_components(def_parser.diearea[1], CELL_HEIGHT,
                                        def_parser.components.comps)
    num_rows = len(components)
    # print the sorted components
    correct = 0
    total_cells = 0
    predicts = []
    actuals = []
    # via_groups is only one row
    # for i in range(len(via1_sorted)):
    for i in range(0, 1):
        via_groups = util.group_via(via1_sorted[i], 3, MAX_DISTANCE)
        visited_vias = [] # later, make visited_vias a set to run faster
        cells_pred = []
        for each_via_group in via_groups:
            first_via = each_via_group[0][0]
            # print (first_via)
            if not first_via in visited_vias:
                best_group, prediction = predict_cell(each_via_group, i,
                                                      logit_model, lef_parser)
                print (best_group)
                print (labels[prediction])
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

        num_correct, num_cells = predict_score(cells_pred, actual_comp)

        correct += num_correct
        total_cells += num_cells
        predicts.append(cells_pred)
        actuals.append(actual_comp)

        print ()

    print (correct)
    print (total_cells)
    print (correct / total_cells * 100)


def load_data_pickle(filename):
    try:
        with open(filename, 'rb') as f:
            dataset = pickle.load(f)
    except Exception as e:
        print('Unable to read data from', filename, ':', e)
    return dataset


def old_main_class():
    num_cells_required = 900
    # merge_data()
    # load data from selected pickle
    set_filename = "./merged_data/selected_10_17_16.pickle"
    dataset = load_data_pickle(set_filename)

    # build the numpy array
    label_to_num = {'AND2X1': 0, 'INVX1': 1, 'INVX8': 2, 'NAND2X1': 3,
                    'NOR2X1': 4, 'OR2X1': 5}

    num_to_label = {0: 'AND2X1', 1: 'INVX1', 2: 'INVX8', 3: 'NAND2X1',
                    4: 'NOR2X1', 5: 'OR2X1'}

    # train_model()

    #######
    # DO SOME PREDICTION
    def_path = './libraries/layout_freepdk45/c880a.def'
    def_parser = DefParser(def_path)
    def_parser.parse()
    scale = def_parser.scale

    lef_file = "./libraries/FreePDK45/gscl45nm.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    print ("Process file:", def_path)
    CELL_HEIGHT = int(float(scale) * lef_parser.cell_height)
    all_via1 = util.get_all_vias(def_parser, via_type="M2_M1_via")
    # print (all_via1)
    # sort the vias by row
    via1_sorted = util.sort_vias_by_row(def_parser.diearea[1], CELL_HEIGHT, all_via1)

    MAX_DISTANCE = 2280 # OR2 cell width, can be changed later

    # predict_row()


    ################
    # new section
    # FIXME: need to build the netlist


    # test the image-based method

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


# Main Class
if __name__ == '__main__':
    random.seed(12345)
    # train the model

