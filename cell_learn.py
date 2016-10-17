"""
Train a ML model to predict cells based on vias location

Name: Tri Minh Cao
Email: tricao@utdallas.edu
Date: October 2016
"""

import pickle
import random
import os

# idea: get 900 cells from each type
# separate all data into bins labeled by macro name (AND2, INVX1, etc.)
# when I train, I will select randomly samples from those bins


def merge_data():
    random.seed(12345)
    num_cells_required = 900

    all_samples = []
    all_labels = []

    pickle_folder = "./training_data"
    pickle_files = os.listdir(pickle_folder)
    # print (pickle_files)
    for file in pickle_files:
        # pickle_file = "./training_data/c1355.def.pickle"
        pickle_file = os.path.join(pickle_folder, file)
        try:
            with open(pickle_file, 'rb') as f:
                dataset = pickle.load(f)
        except Exception as e:
            print('Unable to read data from', pickle_file, ':', e)
        all_samples.extend(dataset[0])
        all_labels.extend(dataset[1])

    all_dataset = (all_samples, all_labels)
    # pickle the merged data
    set_filename = "./merged_data/freepdk45_10_17_16.pickle"
    try:
        with open(set_filename, 'wb') as f:
            pickle.dump(all_dataset, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', set_filename, ':', e)

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
        if len(dataset[label]) < 900:
            dataset[label].append(features)
        cont = False
        for each_macro in dataset:
            if len(dataset[each_macro]) < 900:
                cont = True
        if not cont:
            break

    for each_macro in dataset:
        print (each_macro)
        print (len(dataset[each_macro]))

    # pickle the selected data
    set_filename = "./merged_data/selected_10_17_16.pickle"
    try:
        with open(set_filename, 'wb') as f:
            pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', set_filename, ':', e)


# Main Class
if __name__ == '__main__':
    random.seed(12345)
    num_cells_required = 900

    #merge_data()

