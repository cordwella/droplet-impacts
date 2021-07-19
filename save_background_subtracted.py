"""
Save a nice version of a video with background subtraction
"""
from analyse_drop_fall import constants
from analyse_drop_fall.load_data import load_data

import matplotlib.pyplot as plt
from matplotlib import animation


def save_background_subtracted(filename, startframe, noframes, outputfilename,
                               config):
    # open video_
    frame_array = load_data(filename, config)


    frame_array = frame_array[0][startframe:startframe + noframes]
    fig = plt.figure(figsize=(6, 10))
    plt.tight_layout()
    frames = []
    ax = plt.gca()
    ax.set_axis_off()
    for i in frame_array:
        frames.append([plt.imshow(i, cmap='gray', animated=True)])

    ani = animation.ArtistAnimation(fig, frames, interval=75, blit=True,
                                    repeat_delay=1000)
    ani.save(outputfilename)
    # plt.show()

def save_background_subtracted_windows(filename, startframe, noframes, outputfilename,
                               config):
    # open video_
    frame_array = load_data(filename, config)


    frame_array = frame_array[0][startframe:startframe + noframes]

    width, height, channels = frame_array[0].shape
    # x = np.array([[frame, frame, frame] for frame in video_frames])
    # print(x.shape)
    fps = 24
    clip = moviepy.editor.VideoClip(lambda i: frame_array[int(i*fps)], duration=len(frame_array)/fps)
    clip.write_videofile(save_filename, fps=fps)

if __name__ == '__main__':
    startframe = 0  # int(input("Start frame wrt to output labelling"))
    noframes = 50 # int(input("Number of frames"))
    filename = input("Filename")
    output_save_filename = input("Output filename")

    save_background_subtracted_windows(filename, startframe, noframes,
                               output_save_filename,
                               constants.ConfigurationDecember9)
    # use analyse drop fall to open and clean video

    # crop video time
    # save it
