"""
Display helper functions for drop fall analysis

Config should be the last parameter in all of them, and plt.show()
should be called afterwards
"""

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np


def display_video_with_com(frame_arrays,
                           frame_data, config):

    fig, ax = plt.subplots(1, len(frame_arrays), sharey='all', sharex='all')

    def loop_frame(i):
        comx = frame_data['frame_data'][i, 1]/config.PIXELS_TO_METERS
        comy = frame_data['frame_data'][i, 0]/config.PIXELS_TO_METERS

        for n in range(len(frame_arrays)):
            ax[n].clear()
            if n == 0:
                # first frame is full 0 - 255
                ax[0].imshow(frame_arrays[0][i], cmap='gray')
            else:
                # all other frames are boolean
                ax[n].imshow(frame_arrays[n][i] * 255, cmap='gray')

            # comx and comy are in meters, however to
            # display on the video that has to be converted
            # back into pixels

            ax[n].scatter(comx, comy, marker='x', label="CoM")

            ax[n].legend(loc='upper left')
            ax[n].set_title(i)

    ani = animation.FuncAnimation(fig, loop_frame, frames=len(frame_arrays[0]) - 1,  # noqa
                                  interval=50)
    return ani


def graph_velocities_and_length(full_frame_data, config):
    fig, ax = plt.subplots(1, 4, sharex='all')

    # plot velocities as a function of time
    times = np.arange(
        len(full_frame_data['frame_data']))/config.FRAMES_PER_SECOND
    # velocity_times = times + .5/FRAMES_PER_SECOND
    velocity_times = times[1:]
    ax[0].plot(velocity_times, full_frame_data['velocities']['com'],
               label="CoM Velocity")
    ax[0].plot(velocity_times, full_frame_data['velocities']['comx'],
               label="CoM x Velocity")
    ax[0].plot(velocity_times, full_frame_data['velocities']['tip'],
               label="Tip Velocity")
    ax[0].plot(velocity_times, full_frame_data['velocities']['top'],
               label="Top Velocity")
    ax[0].set_xlabel("Time (seconds)")
    ax[0].set_ylabel("Velocity (meters/second)")

    # TODO: subplot titles and legends
    ax[0].set_title("Droplet velocity (m/s)")
    ax[0].legend()

    ax[1].plot(times, full_frame_data['frame_data'][:, 4],
               label="Droplet Diameter")
    ax[1].plot(times, full_frame_data['frame_data'][:, 5],
               label="Droplet Length")

    ax[1].plot(times, full_frame_data['contact_width'],
               label='Contact Width')
    print(full_frame_data['contact_width'])
    ax[1].set_title("Droplet size (m)")
    plt.axis([None, None, 0, 2e-8])
    ax[1].legend()

    ax[2].plot(velocity_times, full_frame_data['weber_numbers']['report'],
               label="Weber number (report)")
    ax[2].plot(velocity_times, full_frame_data['weber_numbers']['first_princ'],
               label="Weber number (first principles)")
    ax[2].plot(velocity_times,
               full_frame_data['weber_numbers']['first_princ_conical'],
               label="Weber number (first principles + conical area)")

    ax[2].set_title("Weber Number")
    ax[2].set_xlabel("Time (seconds)")
    ax[2].legend()

    ax[3].plot(times, full_frame_data['frame_data'][:, 6], label="Volume")
    ax[3].plot(times, full_frame_data['frame_data'][:, 7],
               label="Volume (Ellipsoid)")
    ax[3].plot(times, full_frame_data['frame_data'][:, 9],
               label="Volume (Conical sections)")
    ax[1].set_xlabel("Time (seconds)")
    ax[3].legend()

    ax[3].set_title("Computed Volume")

    # plt.show()


def display_frame_and_surrounding(frames, frame_number, config, title=None):
    fig, ax = plt.subplots(1, 5, sharey='all', sharex='all')

    ax[0].imshow(frames[frame_number - 3], cmap='gray')
    ax[0].set_title("3 behind")

    ax[1].imshow(frames[frame_number], cmap='gray')
    if title is not None:
        ax[1].set_title(title)

    ax[2].imshow(frames[frame_number + 3], cmap='gray')
    ax[2].set_title("3 ahead")

    ax[3].imshow(frames[frame_number + 5], cmap='gray')
    ax[3].set_title("5 ahead")

    ax[4].imshow(frames[frame_number + 9], cmap='gray')
    ax[4].set_title("9 ahead")
