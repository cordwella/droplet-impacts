"""
Helper code to get some nice top down videos

Going to modify the load data function to just do the cropping and
background subtraction.

Compare with the start frame for the related side view to get the start
frame, then crop background subtract etc etc.

Frame offset is only used in load_data and only saved in the CSV file ugh

"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import moviepy.editor

# MODIFY THESE
input_file = r"C:\Users\acor102\Documents\ferrofluids\data\amelia_data\7-jan\touch\dist_-570_20200107_171928_C2\dist_-570_20200107_171928_C2.avi"

# input_file = r"C:\Users\acor102\Documents\ferrofluids\data\amelia_data\9-dec\SM_11.5mm_sd\dist_-750_spread_C2\dist_-750_spread_C2.avi"
input_file = r"\\files.auckland.ac.nz\research\ressci201800021-ferrofluids\Phase plot data\Needle\No Magnet\t10c1_C1"
display = False
crop = (0, 200, 670, 850)
save_filename = 'SM_54.55mm_-720_crown_C2.mp4'
frame_start = 4



# core/general function
def open_crop_clean(filename, frame_start=1, crop=None, load_offset=1,
                    max_frames=100, subtract_background=False):
    frame_array = []

    vidcap = cv2.VideoCapture(filename)
    count = 0
    success = True
    background_image = None

    success, image = vidcap.read()

    while load_offset > 0:
        success, image = vidcap.read()
        load_offset = load_offset - 1

    while success and len(frame_array) <= max_frames:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            break

        # transform image to only get the first color value
        image = image[:, :]  # black and white single channel image

        if crop:
            image = image[crop[0]:crop[2],
                          crop[1]:crop[3], :]

        if background_image is None:
            background_image = image
        count += 1

        if count < frame_start:
            continue

        if subtract_background:
            # standard background subtraction
            # divide by two as images are non negative append otherwise
            # there are weird wrap around effects
            t = background_image/2 - image/2
            t[t < 0] = 0

            a= (255 - 2*t)

            #alpha = 1.3
            #beta = -145
            #image = cv2.convertScaleAbs(a, alpha=alpha, beta=beta)
            # image[1.2*a <= a] = 255
            image = a
        frame_array.append(image)
        print(count)

    vidcap.release()
    return frame_array

# open the csv
video_frames = open_crop_clean(input_file, frame_start=frame_start, crop=crop)
# get the matching row

if display:
    fig= plt.figure()
    ax = plt.gca()
    plt.tight_layout()

    def loop_frame(i):
        ax.imshow(video_frames[i][:, :, 0], cmap='gray')

        # comx and comy are in meters, however to
        # display on the video that has to be converted
        # back into pixels
        ax.set_title(i)

    ani = animation.FuncAnimation(fig, loop_frame,
                                  frames=len(video_frames) - 1,  # noqa
                                  interval=2)
    plt.show()


if save_filename:
    width, height, channels = video_frames[0].shape
    # x = np.array([[frame, frame, frame] for frame in video_frames])
    # print(x.shape)
    fps = 24
    clip = moviepy.editor.VideoClip(lambda i: video_frames[int(i*fps)], duration=len(video_frames)/fps)
    clip.write_videofile(save_filename, fps=fps)

    #out = cv2.VideoWriter(save_filename, cv2.VideoWriter_fourcc(*'MJPG'), 24,
    #                      (width, height))
    #for frame in video_frames:
        #gray_3c = cv2.merge([frame, frame, frame])
        #out.write(frame)
    #out.release()
