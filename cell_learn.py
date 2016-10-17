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


# Main Class
if __name__ == '__main__':
    random.seed(12345)
    num_cells_required = 900

    all_samples = []
    all_labels = []

    pickle_folder = "./training_data"
    pickle_files = os.listdir(pickle_folder)
    print (pickle_files)
    # pickle_file = "./training_data/c1355.def.pickle"
    # try:
    #     with open(pickle_file, 'rb') as f:
    #         dataset = pickle.load(f)
    # except Exception as e:
    #     print('Unable to read data from', pickle_file, ':', e)
    #
    # print (dataset[0])
    # print (dataset[1])

