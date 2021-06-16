# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 18:33:03 2020

@author: acor102

run v2 -> runs twice with two configurations to allow two different settings 
should be used for a proper contact line run and then a volume estimator run
"""

import constants
from main import process_side_video
import datetime
import sys

csv_filename = "C:/Users/acor102/Documents/ferrofluids data/output-repeats.csv" # noqa
filename = "file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/6-jan/from_top_7.2mm/dist_-800_spread_20200106_163252_C2/dist_-800_spread_20200106_163252_C2.avi"
data_save_filename = None # filename.replace("file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/", "C:/Users/acor102/Documents/ferrodata/").replace(".avi", ".p") # noqa
field_id = filename.split("/")[-3] # noqa


configuration1 = constants.ConfigurationJan7()
configuration2 = constants.ConfigurationJan7()
configuration2.THRESHOLD_LEVEL = configuration2.VOLUME_THRESHOLD_LEVEL
configuration2.MAXIMUM_FRAME_NO = configuration2.VOLUME_MAXIMUM_FRAME_NO

field = configuration1.MAGNETIC_FIELDS[field_id]

summary, frame_offset, line = process_side_video(
    filename, configuration1, save_filename=data_save_filename)

sys.exit()

# run again with proper thresholding to get correct 
# weber and volume numbers 
# TODO: find out how much this changes my values as it 
# will double the computational analysis time
summary2, frame_offset, line = process_side_video(
    filename, configuration2, contact_line=line) # graphs=False

summary = list(summary)

classification_definitions = """
cs = classical splash
cd = classical deposition
cc = classical crown instabilities
rs = rosensweig splash
rd = rosensweig after deposition
rcr = rosensweig after crown and retraction
rcd = rosensweig unsure if c or d
rc = rosensweig forms directly on crown instabilities
ri = rosensweig immediate
rcu = rosensweig crown, but not clear further
ru = rosensweig uncertain of classificaiton
u = unknown
o = other

i = ignore dont write anything
append v on the end to not the velocity might not be great
"""
print(classification_definitions)
comment = input("Video classification: ")
while len(comment) == 0:
    comment = input("Video classification: ")

#if #comment[0] == 'i':
sys.exit()


# classification details
# s = splash
# r = clean rim / spread
# c = crown instabilities
# cr = crown instabilties with retraction before formation
# rr = rosensweig spikes form immediately at rim


d = datetime.datetime.now().strftime("%I:%M%p %B %d %Y")

# add some adminy stuff to this
help_summary = [filename, d, configuration1.__class__.__name__, field_id, field,
                frame_offset, comment]
t = [str(i) for i in help_summary + summary + summary2]

print("Field (T)", field)
print("Filename", filename)
# write to csv file
full = ",".join(t) + "\n"

print(full)
with open(csv_filename, 'a') as f:
    f.write(full)
