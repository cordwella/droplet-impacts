# Copy files over but only the ones we need

import os
from shutil import copyfile
# start folder
start_folder = r"\\files.auckland.ac.nz\research\ressci201800021-ferrofluids\Alex\Ferrodata"
copy_to_folder = "C:/Users/acor102/Documents/ferrofluids/data/alex_data/"

# require filenames to end in this before copying
use_filenames = "_C2.avi"
# print(list(os.walk(start_folder)))

for fn in os.walk(start_folder):
    for filename in fn[2]:
        if filename.endswith(use_filenames):
            full_orig_name = fn[0] + "/" + filename
            save_name = fn[0].replace(start_folder, copy_to_folder) + "/" + filename
            if os.path.isfile(save_name):
                print("File already exists")
                continue

            if not os.path.exists(os.path.dirname(save_name)):
                print(os.path.dirname(save_name))
                os.makedirs(os.path.dirname(save_name))
            print("Copy {} -> {}".format(full_orig_name, save_name))
            copyfile(full_orig_name, save_name)
