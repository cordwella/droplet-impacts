import constants
from main import process_side_video
import datetime
import sys
from file_list import file_list
import os

csv_filename = "C:/Users/acor102/Documents/ferrofluids/FIXED_summary.csv" # noqa
csv_filename = "C:/Users/acor102/Documents/ferrofluids/alex_summary_second_run_1.csv" # noqa

#filename = r"C:\Users\acor102\Documents\ferrofluids\data\amelia_data\6-jan\from_top_4.0mm\dist_-740_crown_20200106_170923_C2\dist_-740_crown_m_20200106_170923_C2.avi"

#filename = r"C:\Users\acor102\Documents\ferrofluids\data\amelia_data\6-jan\from_top_7.2mm\dist_-800_spread_20200106_163252_C2\dist_-800_spread_20200106_163252_C2.avi"

#data_save_filename = filename.replace(r"C:\Users\acor102\Documents\ferrofluids\data\amelia_data",
#                                      "C:/Users/acor102/ferrofluids/data/Amelia/").replace(".avi", ".p") # noqa
#filename = "file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Alex/Ferrodata/Jan12-13/H660mm/H660mm_M3063_1_C2/H660mm_M3063_1_C2.avi"
#data_save_filename = filename.replace("file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Alex/Ferrodata/",
#                                       "C:/Users/acor102/Documents/ferrofluids/data/Alex/").replace(".avi", ".p") # noqa

# check top down video

use_filenames = "_C2.avi"

# folder name, then config and magnet distance calculation
alex_magnet_height = lambda x: 35.61 - (float(x.split("_")[-3][1:])/100)

config_to_use = {
    # amelia stuff
    '6-jan': (constants.ConfigurationJan67, lambda x: float(x.split("_")[3].split("\\")[0][:-2]) + 1),
    '7-jan': (constants.ConfigurationJan7, lambda x: float(x.split("_")[3].split("\\")[0][:-2]) + 1),
    '9-dec': (constants.ConfigurationDecember9, lambda x: float(x.split("_")[2].split("\\")[0][:-2]) + 7.45),
    '19-dec': (constants.ConfigurationDec19, lambda x: float(x.split("-")[2].split("\\")[0][:-2]) + 7.45),
    # alexs stuff
    'Dec10-11': (constants.ConfigurationDec10_2020, alex_magnet_height),
    'Jan12-13': (constants.ConfigurationJan12_2021, alex_magnet_height),
    'Jan27-28': (constants.ConfigurationJan27_2021, alex_magnet_height),
    'May2021': (constants.ConfigurationMay2021, alex_magnet_height),
}

for fn in file_list:
    data_save_filename = fn.replace("C:\\Users\\acor102\\Documents\\ferrofluids\\data\\",
                                    "C:\\Users\\acor102\\Documents\\ferrofluids\\data\\pickled_two\\").replace(".avi", ".p") # noqa

    #data_save_filename = data_save_filename.replace(
    #    "C:/Users/acor102/Documents/ferrofluids/data\\",
    #    "C:/Users/acor102/ferrofluids/data/pickled/")

    if 'alex' not in fn:
        continue
    if 'Dec' in fn:
        continue
    if os.path.exists(data_save_filename):
        #print("Processing already completed")
        continue
    if "_m_" in fn.split("\\")[-1]:
        #print("Modified speed file")
        continue

    # ID to use
    config_id = fn.split("\\")[7]
    configuration, mag_lambda = config_to_use[config_id]
    if 'touch' in fn:
        magnet_height = 2
    else:
        magnet_height = mag_lambda(fn)

    print(fn, magnet_height, configuration.__name__, data_save_filename)

    # find mag field
    try:
        summary, frame_offset, line = process_side_video(
            fn, configuration, save_filename=data_save_filename, graphs=True)
    except IndexError as e:
        print(e)
        continue

    summary = list(summary)

    classification_definitions = """"""
    print(classification_definitions)
    #comment = 'u' # unknown, automatic
    comment = input("Video classification: ")

    if comment and comment[0] == 'r':
        summary, frame_offset, line = process_side_video(
            fn, configuration, save_filename=None, graphs=True)
        comment = input("Video classification: ")
    if comment and comment[0] == 'i':
        continue
    d = datetime.datetime.now().strftime("%I:%M%p %B %d %Y")

    # add some adminy stuff to this
    help_summary = [fn, d, configuration.__name__, magnet_height,
                    frame_offset, comment]
    t = [str(i) for i in help_summary + summary]

    # write to csv file
    full = ",".join(t) + "\r\n"

    print(full)
    with open(csv_filename, 'a') as f:
        f.write(full)
