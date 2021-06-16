"""
Generate csv summary files for a folder of drop impacts at a specific magnet
specification

Does standard stuff, and then allows comments on each of them
general classification -> splash/crown/rim/other classification
classifications:

low b:
deposition, deposition rim instablilites, splash

mid b:
deposition -> rosensweig, deposition smooth rim -> rosensweig,
deposition rim instabilities -> rosensweig, splash -> rosensweig

high b:
deposition/smooth rim -> rosensweig -> outer rim,
deposition splash rim -> outer rim,
no pre rosensweig formation before rim

(this is a selection, and goes in one frame)

other notes are:
nice visualisation top
nice visulasation bottom

All of the notes here should be categories and general notes and screen shots

Do I also save background subtraction videos?
this would be quite good because they would also start from useful spots
leave background subtraction saving as an option -> im running out of hard
disk space, so can't save every thing

this be the option to only save

command for going frame by frame through the video -> melt, intend to
save background subtracted video iff the video is nice and has nice features
for displaying inducidual frames

Due to size issues, and also interesting shapes im seeing, I also really
want to save the tracking pickle of full frames data
different regimes have different shapes of interesting things
"""

from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askfloat, askstring

if __name__ == '__main__':
    folder = askdirectory(title="Droplet Folder")

    # replace folder output folder thing based on my details

    outputfolder = askstring("Output folder", "Output folder",
                             initialvalue=folder)
    # append = input("Append to existing file?")

    magnetic_field_strength = askfloat("Magnetic field",
                                       "Magnetic Field in Tesla")

    configuration = askstring("Configuration Object",
                              "Configuration Object code")

    print(folder, outputfolder, magnetic_field_strength, configuration)
    # print list of things
    # print check

    # open folder and go through all files

    # display file, display
