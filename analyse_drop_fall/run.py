import constants
from main import process_side_video
import datetime
import sys
from file_list import file_list
import os

csv_filename = "C:/Users/acor102/Documents/ferrofluids/FIXED_summary.csv" # noqa
filename = "C:\\Users\\acor102\\Documents\\ferrofluids\\data\\alex_data\\May2021\\H260mm_M3353_1_C2\\H260mm_M3353_1_C2.avi"

filename = r"\\files.auckland.ac.nz\research\ressci201800021-ferrofluids\Phase plot data\Needle\No Magnet\t20c1_C1\t20c1_C1.avi"

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

data_save_filename = filename.replace("C:\\Users\\acor102\\Documents\\ferrofluids\\data\\",
								"C:\\Users\\acor102\\Documents\\ferrofluids\\data\\pickled\\").replace(".avi", ".p") # noqa


# ID to use
# config_id = filename.split("\\")[7]
# configuration, mag_lambda = config_to_use[config_id]
configuration = constants.ConfigurationStephen
#if 'touch' in filename:
#	magnet_height = 2
#else:
#	magnet_height = mag_lambda(filename)
magnet_height = 23

print(filename, magnet_height, configuration.__name__, data_save_filename)

# find mag field
summary, frame_offset, line = process_side_video(
	filename, configuration, save_filename=None, graphs=True)

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
comment = 'i' # unknown, automatic
if comment[0] == 'i':
	sys.exit()
d = datetime.datetime.now().strftime("%I:%M%p %B %d %Y")

# add some adminy stuff to this
help_summary = [filename, d, configuration.__name__, magnet_height,
				frame_offset, comment]
t = [str(i) for i in help_summary + summary]

# write to csv file
full = ",".join(t) + "\r\n"

#print(full)
#with open(csv_filename, 'a') as f:
#	f.write(full)
