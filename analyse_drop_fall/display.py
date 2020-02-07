"""
Display helper functions for drop fall analysis

Config should be the last parameter in all of them, and plt.show()
should be called afterwards
"""

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np


def display_video_with_com(frame_arrays,
                           frame_data, config, line=None):

    fig, ax = plt.subplots(1, len(frame_arrays), sharey='all', sharex='all')
    plt.tight_layout()

    if line is not None:
        xp = np.linspace(0, frame_arrays[0][0].shape[1] - 1, 100)
        y = line(xp)

    def loop_frame(i):
        comx = frame_data['frame_data'][i, 1]/config.PIXELS_TO_METERS
        comy = frame_data['frame_data'][i, 0]/config.PIXELS_TO_METERS

        for n in range(len(frame_arrays)):
            ax[n].clear()
            if line is not None and config.DISPLAY_CONTACT_LINE:
                ax[n].plot(xp, y, label='Contact Line')
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
                                  interval=25)
    return ani


def graph_velocities_and_length(full_frame_data, config):
    fig, ax = plt.subplots(2, 3) #, sharex='all')
    fig.tight_layout()

    pre_impact_time = (
        full_frame_data['pre_impact_frame']/config.FRAMES_PER_SECOND)
    max_spread_time = (
        full_frame_data['max_spread_frame']/config.FRAMES_PER_SECOND)
    max_diameter_time = (
        full_frame_data['max_diameter_frame']/config.FRAMES_PER_SECOND)
    # plot velocities as a function of time
    times = np.arange(
        0, len(full_frame_data['frame_data']), 1)/config.FRAMES_PER_SECOND
    # velocity_times = times
    velocity_times = times[:-1] #  + .5/config.FRAMES_PER_SECOND
    ax[0, 0].plot(velocity_times, full_frame_data['velocities']['com'],
                  label="CoM Velocity")
    ax[0, 0].plot(velocity_times, full_frame_data['velocities']['comx'],
                  label="CoM x Velocity")
    ax[0, 0].plot(velocity_times, full_frame_data['velocities']['tip'],
                  label="Tip Velocity")
    ax[0, 0].plot(velocity_times, full_frame_data['velocities']['top'],
                  label="Top Velocity")
    ax[0, 0].axvline(x=pre_impact_time, label='Pre Impact Time',
                     color='black')
    ax[0, 0].set_xlabel("Time (seconds)")
    ax[0, 0].set_ylabel("Velocity (meters/second)")

    # TODO: subplot titles and legends
    ax[0, 0].set_title("Droplet velocity (m/s)")
    ax[0, 0].legend()

    ax[0, 1].plot(times, full_frame_data['frame_data'][:, 4],
                  label="Droplet Diameter")
    # ax[0, 1].plot(times, full_frame_data['frame_data'][:, 5],
    #           label="Droplet Length")
    ax[0, 1].plot(times, full_frame_data['reflect_cleaned_heights'],
                  label="Droplet Length / Height")

    ax[0, 1].plot(times, full_frame_data['contact_width'],
                  label='Contact Width')
    ax[0, 1].axvline(x=max_spread_time, label='Maximum Spread',
                     color='grey')
    ax[0, 1].axvline(x=max_diameter_time, label='Maximum Diameter',
                     color='#a0a0a0')
    ax[0, 1].axvline(x=pre_impact_time, label='Pre Impact Time',
                     color='black')
    ax[0, 1].set_xlabel("Time (seconds)")
    ax[0, 1].set_ylabel("Length (meters)")

    ax[0, 1].set_title("Droplet size (m)")
    plt.axis([None, None, 0, 2e-8])
    ax[0, 1].legend()

    ax[1, 1].plot(velocity_times,
                  full_frame_data['weber_numbers']['first_princ_conical'],
                  label="Weber number \n(Conical area)")
    ax[1, 1].plot(velocity_times,
                  full_frame_data['weber_numbers']['fixed_volume'],
                  label="Weber number \n(Fixed Volume)")
    ax[1, 1].plot(velocity_times,
                  full_frame_data['weber_numbers']['tip'],
                  label="Weber number \n(Tip Velocity)")
    ax[1, 1].axvline(x=pre_impact_time, label='Pre Impact Time',
                     color='black')

    ax[1, 1].set_title("Weber Number")
    ax[1, 1].set_xlabel("Time (seconds)")
    ax[1, 1].legend()

    ax[1, 0].plot(times, full_frame_data['frame_data'][:, 6], label="Volume")
    ax[1, 0].plot(times, full_frame_data['frame_data'][:, 7],
                  label="Volume (Ellipsoid)")
    ax[1, 0].plot(times, full_frame_data['frame_data'][:, 9],
                  label="Volume (Conical sections)")
    ax[1, 0].axvline(x=pre_impact_time, label='Pre Impact Time',
                     color='black')

    ax[1, 0].set_xlabel("Time (seconds)")
    ax[1, 0].legend()

    ax[1, 0].set_title("Computed Volume")

    ax[0, 2].plot(times, full_frame_data['solidity'],
                  label="Solidity (area/convex area)")
    ax[0, 2].axvline(x=max_spread_time, label='Maximum Spread',
                     color='grey')
    ax[0, 2].axvline(x=pre_impact_time, label='Pre Impact Time',
                     color='black')
    ax[0, 2].legend()
    # ax[1, 1].set_ylim([0, 1])
    ax[0, 2].set_title("Solidity")

    ax[1, 2].clear()

    # plt.show()


def display_frame_and_surrounding(frames, frame_number, config, title=None):
    fig, ax = plt.subplots(1, 6, sharey='all', sharex='all')

    ax[0].imshow(frames[frame_number - 3], cmap='gray')
    ax[0].set_title("3 behind")

    ax[1].imshow(frames[frame_number - 2], cmap='gray')
    ax[1].set_title("2 behind")

    ax[2].imshow(frames[frame_number - 2], cmap='gray')
    ax[2].set_title("1 behind")

    ax[3].imshow(frames[frame_number], cmap='gray')
    if title is not None:
        ax[3].set_title(title)

    ax[4].imshow(frames[frame_number + 1], cmap='gray')
    ax[4].set_title("1 ahead")

    ax[5].imshow(frames[frame_number + 3], cmap='gray')
    ax[5].set_title("3 ahead")
