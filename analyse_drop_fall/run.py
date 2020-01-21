import constants
from main import process_side_video
import datetime

csv_filename = "/home/amelia/Documents/ferrofluids/big data/data/data_summary.csv" # noqa
filename = "/home/amelia/Documents/ferrofluids/big data/videos/amelia/9-dec/SM_6.5mm_sd/dist_-750_spread_C2/dist_-750_spread_C2.avi" # noqa
data_save_filename = filename.replace("/videos/", "/data/").replace(".avi", ".p") # noqa
field_id = "SM_6.5mm_sd" # noqa


# check top down video
print("melt \"{}\"".format(filename.replace("C2", "C1")))

configuration = constants.ConfigurationDecember9

field = configuration.MAGNETIC_FIELDS[field_id]

# find mag field
summary, frame_offset = process_side_video(
    filename, configuration, save_filename=data_save_filename)

summary = list(summary)
comment = input("Video classification (sp/rim/ir/u/o)")

# classification details
# sp = splash
# rim = clean rim
# ir = instabilities (at initial max spread)
# irr = instabilities (at initial max spread, clearly rosensweig)
# u = can't accurately identify between rim and instabilities
# o = other

d = datetime.datetime.now().strftime("%I:%M%p %B %d %Y")

# add some adminy stuff to this
help_summary = [filename, d, configuration.__name__, field_id, field,
                frame_offset, comment]
t = [str(i) for i in help_summary + summary]

print("Field (T)", field)
print("Filename", filename)
# write to csv file
full = ",".join(t) + "\r\n"

print(full)
with open(csv_filename, 'a') as f:
    f.write(full)
