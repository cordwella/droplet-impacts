"""
A modified version of Stephen Chung's code for extracting
the velocities and Weber number of a ferrofluid droplet
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2

# Configurable constants
THRESHOLD_LEVEL = 50  # thresholding the image to pick up the drop
CROP_DIMENSIONS = None  # crop the image to these dimensions
                        # (xstart, ystart, xend, yend)
                        # standard numpy array rules
DENSITY = 1210       # The density of the ferrofluid (kg/m^3)
SURFACE_TENSION = 0.026  # The surface tension of the ferrofluid
                        # I cant remember the units
PIXELS_TO_MM = 0.028563817267384453
PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)
                        # Conversion from pixels to meters
                        # based on the slide in use
                        # might be automated later
FRAMES_PER_SECOND = 2000
# possibly best to take this from the configuration
# files from PFV

# Later on this should be stdin, or called from an actual function#
# videodirectory = input("Enter video directory")

filename = "/home/amelia/Documents/ferrofluids/from server/Magnet/Sm_23mm/11018_C2/11018_C2.avi"

# filename = videodirectory + "/" + videodirectory.split("/")[1] + '/avi'
# startingframe = int(input("Enter the first frame with the entire drop: "))
# endingframe = int(input("Enter the last frame before impact:"))

startingframe = 11
endingframe = 30


plt.style.use('ggplot')


def open_video(filename, startingframe, endingframe):
    frame_array = []
    threshold_frame_array = []

    vidcap = cv2.VideoCapture(filename)

    count = 1
    success = True

    while success and count <= endingframe:
        # write files to frames
        success, image = vidcap.read()
        # TODO: ensure is black and white images
        count += 1
        if count >= startingframe:
            # TODO(amelia): subtract background ?
            # does a background image exist for all of these?
            # transform image to only get the first color value

            image = image[:, :, 0]  # black and white single channel image

            # If a background image has been taken this shouldn't
            # be nessecary
            if CROP_DIMENSIONS:
                image = image[CROP_DIMENSIONS[0]:CROP_DIMENSIONS[2],
                              CROP_DIMENSIONS[1]:CROP_DIMENSIONS[3]]
            frame_array.append(image)
            threshold_frame_array.append((image < THRESHOLD_LEVEL).astype(int))

    # check on this video to make sure it looks right
    # maybe by saving this?
    return frame_array, threshold_frame_array


def get_droplet_positions(threshold_frame):
    # get the 'corner' positions of the droplet in a thresholded
    # frame

    # get coordinates
    coords = threshold_frame.nonzero()
    # find min/max y value
    minxc = coords[1].argmin()
    maxxc = coords[1].argmax()

    # find min/max x value
    # do I want the full coordinates for this?
    # Ill stick with this for now to compute things

    # for y max and min refer to top and bottom respectively
    maxyc = coords[0].argmin()
    minyc = coords[0].argmax()

    maxx = (coords[0][maxxc], coords[1][maxxc])
    miny = (coords[0][minyc], coords[1][minyc])
    maxy = (coords[0][maxyc], coords[1][maxyc])
    minx = (coords[0][minxc], coords[1][minxc])

    return minx, miny, maxx, maxy


def compute_volume_and_com(threshold_frame, coordinates,
                           return_all=False):
    # part of the reason that that could be an issue is the double
    # droplets in images, leading to two objects on the binary
    # stephens method won't work for this

    # okay so tracing from the bottom, left and upwards
    # along the boundrary until I cross over back to the original points

    starting_position = coordinates[1]
    y_coord = starting_position[0]

    # In this case the contour is defined to try and define the radius
    # at each point to compute the volume

    # algorithm follows
    # starting from the lowest point on the droplet compute the width
    # (or alternatively the left most and rightmost points)
    # put this into an array and move up one pixel
    # if there are no white pixels in the frame finish
    # volume in pixels cubed
    volume = 0
    length = 0
    max_width = 0
    vertical_com_contribution = 0
    horizontal_com_contribution = 0

    while True:
        line = threshold_frame[y_coord, :]
        width = np.count_nonzero(line)
        if width == 0:
            # no longer counting the actual size
            break
        if width > max_width:
            max_width = width
        coords = line.nonzero()[0]

        left_most_pixel = coords.min()
        right_most_pixel = coords.max()
        central_pixel = (left_most_pixel + right_most_pixel)/2

        # compute center of the line
        # compute controbution of this line to both vertical and
        # horizontal COM
        dV = np.pi * (width/2)**2

        vertical_com_contribution += y_coord * dV
        horizontal_com_contribution += central_pixel * dV

        volume += dV
        y_coord -= 1

    # full length of the droplet
    length = starting_position[0] - y_coord
    print("Length {}".format(length))
    print("Maxiumum Width {}".format(max_width))
    print("Volume {}".format(volume))

    # other volume option -> model as an ellipsoid

    # compute COMs from additive things
    vertical_com = vertical_com_contribution/volume
    horizontal_com = horizontal_com_contribution/volume

    # could also report tip position as y_coord?
    # as the ymax position does not accurately represent the
    # tip position

    volume1 = 4/3 * np.pi * (max_width/2)**2 * length/2

    if return_all:
        return (volume, (vertical_com, horizontal_com),
                starting_position[0], y_coord, max_width, length, volume1)

    return volume, (vertical_com, horizontal_com)


def compute_velocity(positions):
    positions = np.array(positions)
    # compute velocities attached to the current frame and the frame
    # before, this will mean that there is a velocity associated with
    # all frames except the first one

    dy = (positions[1:] - positions[:-1])
    velocity = dy * FRAMES_PER_SECOND

    return velocity


def compute_weber_number(velocity, diameter):
    # stephen uses the calculation
    # pi * rho * L * D**2 *v**2/ (area * surface tension)
    # Standard calculation
    return DENSITY * velocity**2 * diameter / SURFACE_TENSION


def display_video_with_com(frames, threshold_frames, frame_data):

    fig, ax = plt.subplots(1, 2, sharey='all', sharex='all')

    def loop_frame(i):
        ax[0].clear()
        ax[1].clear()

        ax[0].imshow(frames[i], cmap='gray')
        ax[1].imshow(threshold_frames[i] * 255, cmap='gray')

        # comx and comy are in meters, however to
        # display on the video that has to be converted
        # back into pixels
        comx = frame_data[i, 2]/PIXELS_TO_METERS
        comy = frame_data[i, 1]/PIXELS_TO_METERS

        ax[0].scatter(comx, comy, marker='x', label="CoM")
        ax[1].scatter(comx, comy, marker='x', label="CoM")

        ax[0].legend()
        ax[1].legend()
        plt.title(i)

    ani = animation.FuncAnimation(fig, loop_frame, frames=len(frames),  # noqa
                                  interval=50)
    plt.show()


def graph_velocities_and_length(frame_data):
    com_velocity = compute_velocity(frame_data[:, 1])
    com_x_velocity = compute_velocity(frame_data[:, 2])
    tip_velocity = compute_velocity(frame_data[:, 3])
    bottom_velocity = compute_velocity(frame_data[:, 4])

    fig, ax = plt.subplots(1, 4, sharex='all')

    # plot velocites as a function of time

    times = np.arange(len(frame_data))/FRAMES_PER_SECOND
    velocity_times = times[:-1] + .5/FRAMES_PER_SECOND
    ax[0].plot(velocity_times, com_velocity, label="CoM Velocity")
    ax[0].plot(velocity_times, com_x_velocity, label="CoM x Velocity")
    ax[0].plot(velocity_times, tip_velocity, label="Tip Velocity")
    ax[0].plot(velocity_times, bottom_velocity, label="Bottom Velocity")
    ax[0].set_xlabel("Time (seconds)")
    ax[0].set_ylabel("Velocity (meters/second)")

    # TODO: subplot titles and legends
    ax[0].set_title("Droplet velocity (m/s)")
    ax[0].legend()

    ax[1].plot(times, frame_data[:, 5], label="Droplet Diameter")
    ax[1].plot(times, frame_data[:, 6], label="Droplet Length")
    ax[1].set_title("Droplet size (m)")
    plt.axis([None, None, 0, 2e-8])
    ax[1].legend()

    # plot the weber number
    diameters = frame_data[1:, 5]
    lengths = frame_data[1:, 3] - frame_data[1:, 4]
    print(lengths)

    # TODO(amelia): Clean this mess up
    # although that might mean changing the way the calculation works
    surface_area = np.pi * diameters/2 * (
        lengths * ((np.arcsin(np.sqrt(1 - diameters**2/lengths))) /
                   (np.sqrt(1 - diameters**2/lengths)))
        + diameters)

    weber_number_report = (np.pi * DENSITY * lengths * diameters**2 *
                           com_velocity**2 /
                           (surface_area * SURFACE_TENSION))

    weber_number_first_princ = 12 * (
        DENSITY * frame_data[1:, 0] *
        com_velocity**2/(surface_area * SURFACE_TENSION))

    # weber_number = compute_weber_number(diameters, com_velocity)
    ax[2].plot(velocity_times, weber_number_report,
               label="Weber number (report)")
    ax[2].plot(velocity_times, weber_number_first_princ,
               label="Weber number (first principles)")

    ax[2].set_title("Weber Number \n(See honours report)")
    ax[2].set_xlabel("Time (seconds)")
    ax[2].legend()

    print("Final Weber Number (first principles) {}".format(
        weber_number_first_princ[-1]))
    print("Final Weber Number (report) {}".format(
        weber_number_report[-1]))

    ax[3].plot(times, frame_data[:, 0], label="Volume")
    ax[3].plot(times, frame_data[:, -1], label="Volume (Ellipsoid)")
    ax[1].set_xlabel("Time (seconds)")
    ax[3].legend()

    ax[3].set_title("Computed Volume")

    plt.show()


frames, threshold_frames = open_video(filename, startingframe, endingframe)

frame_data = []

for frame in threshold_frames:
    positions = get_droplet_positions(frame)

    (volume, com, bottomy, topy,
        diameter, length, volume1) = compute_volume_and_com(
        frame, positions, True)

    frame_data.append([volume, com[0], com[1],
                      bottomy, topy, diameter, length, volume1])

frame_data = np.array(frame_data)
frame_data = frame_data * PIXELS_TO_METERS  # put everything into meters
# convert the volume into meters cubed (from pixels cubed)


frame_data[:, 0] = frame_data[:, 0] * (PIXELS_TO_METERS)**2
frame_data[:, -1] = frame_data[:, -1] * (PIXELS_TO_METERS)**2

# 2 graphing subroutines
# firstly shows the video in both forms with COM highlighted

display_video_with_com(frames, threshold_frames, frame_data)
graph_velocities_and_length(frame_data)

# print weber number
# based on final values?
# or as a function of time?
