import constants
from main import process_side_video
import datetime
import sys
from file_list import file_list
import os

csv_filename = "C:/Users/acor102/Documents/ferrofluids/stephen_summary_new.csv" # noqa

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
start_folder = "\\\\files.auckland.ac.nz\\research\\ressci201800021-ferrofluids\\Phase plot data\\"
for files in os.walk(start_folder):
    for fn in files[2]:
        if 'C2.avi' not in fn:
            continue
        fn = files[0] + "\\" + fn

        data_save_filename = fn.replace("\\\\files.auckland.ac.nz\\research\\ressci201800021-ferrofluids\\Phase plot data\\",
                                        "C:\\Users\\acor102\\Documents\\ferrofluids\\data\\pickled\\stephen\\").replace(".avi", ".p") # noqa
        # data_save_filename = "C:\\Users\\acor102\\Documents\\ferrofluids\\data\\pickled\\stephen\\" + fn.replace(".avi", ".p")
        # if False: # 'alex' not in fn:
        #    continue
        if os.path.exists(data_save_filename):
            #print("Processing already completed")
            # continue
            pass

        configuration = constants.ConfigurationStephen
        print(files)
        if 'No Magnet' in files[0]:
            magnet_height = 100
        else:
            magnet_height = float(files[0].split("_")[1].split('m')[0])
        print(fn, magnet_height, configuration.__name__, data_save_filename)

        # find mag field
        try:
            summary, frame_offset, line = process_side_video(
                fn, configuration, save_filename=data_save_filename, graphs=False)
        except FileNotFoundError: #IndexError as e:
#            print(e)
            continue

        summary = list(summary)

        classification_definitions = """r = rim forms
        nm = no magnetic spikes
        s = spikes form

        i = ignore dont write anything
        anything else is considerd a comment
        append v on the end to not the velocity might not be great
        """
        print(classification_definitions)
        # comment = input("Video classification: ")
        comment = 'u' # unknown, automatic
        if comment[0] == 'i':
            sys.exit()
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
