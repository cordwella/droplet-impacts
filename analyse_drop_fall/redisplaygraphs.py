# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 13:24:54 2020

@author: acor102
"""

# display contact line
import pickle 
from display import graph_velocities_and_length
import constants
from matplotlib import pyplot as plt

filename = "file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/19-dec/from_top-6.2mm/dist_-710_rim_20191220_125009_C2/dist_-710_rim_20191220_125009_C2.avi"
data_save_filename = filename.replace("file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/", "C:/Users/acor102/Documents/amelia_code/ferrodata/").replace(".avi", ".p") # noqa
print(filename)
full_frames_data = pickle.load(open(data_save_filename, 'rb'))


graph_velocities_and_length(full_frames_data, constants.ConfigurationDec19)
plt.show()