Code and required calibration documents are to be saved here

Calibration files and the like should be in their own folders,
however python/matlab files containing computed values can be stored
here. Everything stored here should make sense in a git commit.

Text documents describing file structure is also a good fit for here.

## analyse_drop_fall.py

Details to come

## determine_threshold.py

Determine optimal thresholding for droplet images.

Inputs: File of droplet video, frame number to analyse

It is advisable to run this a few times for differently numbered frames and
to take the average of that. This process can vary wildly dependnig on lots
of things.

# Droplet Analysis

## Usage instructions

First setup your python enviroment. This requires the packages:
- matplotlib
- numpy
- opencv

Edit your copy of analyse_drop_fall to include your own configuration object.
Easiest way to do this is to copy and compare one of the existing objects.
MAGNETIC_FIELDS, THRESHOLD_LEVEL and PIXELS_TO_MM will change for every
setup.

The best threshold can be calculated using the determine_threshold.py script.
You'll know your thresholding is right if your volume stays constant on every
falling frame, and that the black and white images highlight your droplet.
Depending on your background subtraction setup you may need to modify this and
do a second run to get the contact line analysis to run correctly. Thresholding
is calculated differently with and without background subtraction turned on, and
there's a different script for with background subtraction.

Then edit run.py to point at your input file, on line 8 to point at where you
want to output timeseries data for each video and on line 15 to select your
configation object.

Run this code from the directory it's in and hopefully you should get some nice
graphs and images that pop up! (If you don't sucks to be you)

Once all windows are closed the software will ask you for a classification. These
are mostly meaningless at this point but if you dear reader have a standard
human driven classification scheme this is where you should use it.

For all values other than 'i' this will then enter a summary line in a csv file
that you should have setup in the file.


## Code output from run.py
There are 3 forms out output from the main run.py code. A set of interactive
graphs that popup during runtime, a csv output line which contains a summary
and a python pickle file.

Pickle files save python native objects so they can be retrieved later. In this
case it saves mostly the times series data from the main function in process_side_video.
This will only be saved if save_filename is passed as an option.
By default it will save in the same directory structure as the original video, and
internally is made up of a dictionary. This doesn't work for image processing
but is a quick way to calculate/create time series graphs during post analysis.
