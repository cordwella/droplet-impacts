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
CROP_DIMENSIONS = (0, 0, 665, 300)  # crop the image to these dimensions
                        # (ystart, xstart, yend, xend)
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

SUBTRACT_BACKGROUND = False

# possibly best to take this from the configuration
# files from PFV

# Later on this should be stdin, or called from an actual function#
# videodirectory = input("Enter video directory" )

# TODO(amelia): test the surface area calculations against known 'perfect'
# shapes and generate videos
# build checking for when the drop is falling DONE
# compute maximum spread and frame number for maximum spread DONE
# shove up a display of the maximum spread frame not yet
# determine cropping dimensions and bottom dimension for thing done, sort of
#   this is currently determined by
# or do I determine this by position when
# filename = "/home/amelia/Documents/ferrofluids/p01c2_C2.avi"
filename = "/home/amelia/Documents/ferrofluids/from server/Magnet/Sm_23mm/11018_C2/11018_C2.avi"

# filename = videodirectory + "/" + videodirectory.split("/")[1] + '/avi'
# startingframe = int(input("Enter the first frame with the entire drop: "))
# endingframe = int(input("Enter the last frame before impact:"))

# startingframe = 11
endingframe = 300

calculated_starting_frame = None


plt.style.use('ggplot')


def open_video(filename, endingframe):
    frame_array = []
    threshold_frame_array = []

    vidcap = cv2.VideoCapture(filename)

    count = 0
    success = True
    calculated_starting_frame = False
    background_image = None

    while success and count <= endingframe:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            break

        # transform image to only get the first color value
        image = image[:, :, 0]  # black and white single channel image

        # If a background image has been taken this shouldn't
        # be nessecary

        # perform image testing
        if CROP_DIMENSIONS:
            image = image[CROP_DIMENSIONS[0]:CROP_DIMENSIONS[2],
                          CROP_DIMENSIONS[1]:CROP_DIMENSIONS[3]]
        if SUBTRACT_BACKGROUND:
            if background_image is None:
                # first frame is the background image
                background_image = image

            image = abs(image - background_image)
            # todo -> check that this doesn't go negative or do
            # weird things

        threshold_image = (image < THRESHOLD_LEVEL).astype(int)

        if calculated_starting_frame:
            frame_array.append(image)
            threshold_frame_array.append(threshold_image)
        elif threshold_image.any() and not threshold_image[0, :].any():
            # there is a droplet in the frame and it is full in the frame
            calculated_starting_frame = count
            # check for emptiness in the threshold image
            frame_array.append(image)
            threshold_frame_array.append(threshold_image)

        count += 1


    # check on this video to make sure it looks right
    # maybe by saving this?
    # return calculated calculated_starting_frame
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


def compute_droplet_values_single_frame(threshold_frame):
    # part of the reason that that could be an issue is the double
    # droplets in images, leading to two objects on the binary
    # stephens method won't work for this

    # okay so tracing from the bottom, left and upwards
    # along the boundrary until I cross over back to the original points

    coordinates = get_droplet_positions(threshold_frame)

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
    volume_cone = 0
    surface_area_cone = 0
    previous_width = 0

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

        # conical contributions
        dV_conical = 1/3 * np.pi * (previous_width**2 + width**2 +
                                    width*previous_width) / 4
        rad = width/2
        prev_rad = previous_width/2
        dA_conical = np.pi * (prev_rad + rad) * (
                    np.sqrt(1 + (rad - prev_rad)**2))
        surface_area_cone += dA_conical
        volume_cone += dV_conical

        # compute center of the line
        # compute controbution of this line to both vertical and
        # horizontal COM
        dV = np.pi * (width/2)**2

        vertical_com_contribution += y_coord * dV
        horizontal_com_contribution += central_pixel * dV

        previous_width = width
        volume += dV
        y_coord -= 1

    # compute final conical components of surface area and volume
    dV_conical = 1/3 * np.pi * (previous_width**2 + width**2 +
                                width*previous_width) / 4
    rad = width/2
    prev_rad = previous_width/2
    dA_conical = np.pi * (prev_rad + rad) * (
                np.sqrt(1 + (rad - prev_rad)**2))
    surface_area_cone += dA_conical
    volume_cone += dV_conical
    # print(volume_cone)

    # full length of the droplet
    length = starting_position[0] - y_coord
    # print("Length {}".format(length))
    # print("Maxiumum Width {}".format(max_width))
    # print("Volume {}".format(volume))

    # other volume option -> model as an ellipsoid

    # compute COMs from additive things
    vertical_com = vertical_com_contribution/volume
    horizontal_com = horizontal_com_contribution/volume

    # could also report tip position as y_coord?
    # as the ymax position does not accurately represent the
    # tip position

    surface_area_ellipse = np.pi * max_width/2 * (
        length * ((np.arcsin(np.sqrt(1 - max_width**2/length**2))) /
                  (np.sqrt(1 - max_width**2/length**2)))
        + max_width)

    volume_ellipse = 4/3 * np.pi * (max_width/2)**2 * length/2

    # convert to meters

    vertical_com = vertical_com * PIXELS_TO_METERS
    horizontal_com = horizontal_com * PIXELS_TO_METERS
    top_y_coordinate = starting_position[0] * PIXELS_TO_METERS
    bottom_y_coord = y_coord * PIXELS_TO_METERS
    max_width = max_width * PIXELS_TO_METERS
    length = length * PIXELS_TO_METERS

    volume = volume * PIXELS_TO_METERS**3  # cylindrical volume approximation
    volume_ellipse = volume_ellipse * PIXELS_TO_METERS**3
    surface_area_ellipse = surface_area_ellipse

    volume_cone = volume_cone * PIXELS_TO_METERS**3
    surface_area_cone = surface_area_cone * PIXELS_TO_METERS**2

    return (vertical_com, horizontal_com, top_y_coordinate, bottom_y_coord,
            max_width, length,
            volume, volume_ellipse, surface_area_ellipse,
            volume_cone, surface_area_cone)


def compute_velocity(positions):
    positions = np.array(positions)
    # compute velocities attached to the current frame and the frame
    # before, this will mean that there is a velocity associated with
    # all frames except the first one

    dy = (positions[1:] - positions[:-1])
    velocity = dy * FRAMES_PER_SECOND

    return velocity


def display_video_with_com(frames, threshold_frames, frame_data):

    fig, ax = plt.subplots(1, 2, sharey='all', sharex='all')

    def loop_frame(i):
        ax[0].clear()
        ax[1].clear()

        ax[0].imshow(frames[i + 1], cmap='gray')
        ax[1].imshow(threshold_frames[i + 1] * 255, cmap='gray')

        # comx and comy are in meters, however to
        # display on the video that has to be converted
        # back into pixels
        comx = frame_data[i, 1]/PIXELS_TO_METERS
        comy = frame_data[i, 0]/PIXELS_TO_METERS

        ax[0].scatter(comx, comy, marker='x', label="CoM")
        ax[1].scatter(comx, comy, marker='x', label="CoM")

        ax[0].legend()
        ax[1].legend()
        plt.title(i)

    ani = animation.FuncAnimation(fig, loop_frame, frames=len(frame_data),  # noqa
                                  interval=50)
    # plt.show()
    return ani


def graph_velocities_and_length(full_frame_data):
    fig, ax = plt.subplots(1, 4, sharex='all')

    # plot velocites as a function of time
    times = np.arange(len(full_frame_data))/FRAMES_PER_SECOND
    # velocity_times = times + .5/FRAMES_PER_SECOND
    ax[0].plot(times, full_frame_data[:, 11], label="CoM Velocity")
    ax[0].plot(times, full_frame_data[:, 12], label="CoM x Velocity")
    ax[0].plot(times, full_frame_data[:, 13], label="Tip Velocity")
    ax[0].plot(times, full_frame_data[:, 14], label="Top Velocity")
    ax[0].set_xlabel("Time (seconds)")
    ax[0].set_ylabel("Velocity (meters/second)")

    # TODO: subplot titles and legends
    ax[0].set_title("Droplet velocity (m/s)")
    ax[0].legend()

    ax[1].plot(times, full_frame_data[:, 4], label="Droplet Diameter")
    ax[1].plot(times, full_frame_data[:, 5], label="Droplet Length")
    ax[1].set_title("Droplet size (m)")
    plt.axis([None, None, 0, 2e-8])
    ax[1].legend()

    ax[2].plot(times, full_frame_data[:, 15],
               label="Weber number (report)")
    ax[2].plot(times, full_frame_data[:, 16],
               label="Weber number (first principles)")
    ax[2].plot(times, full_frame_data[:, 17],
               label="Weber number (first principles + conical area)")

    ax[2].set_title("Weber Number")
    ax[2].set_xlabel("Time (seconds)")
    ax[2].legend()

    ax[3].plot(times, full_frame_data[:, 6], label="Volume")
    ax[3].plot(times, full_frame_data[:, 7], label="Volume (Ellipsoid)")
    ax[3].plot(times, full_frame_data[:, 9], label="Volume (Conical sections)")
    ax[1].set_xlabel("Time (seconds)")
    ax[3].legend()

    ax[3].set_title("Computed Volume")

    # plt.show()


def display_frame_and_surrounding(frames, frame_number, title=None):
    fig, ax = plt.subplots(1, 3, sharey='all', sharex='all')

    ax[0].imshow(frames[frame_number - 1], cmap='gray')
    ax[1].imshow(frames[frame_number], cmap='gray')
    if title is not None:
        plt.title(title)

    ax[2].imshow(frames[frame_number + 1], cmap='gray')


def process_side_video(filename, configuration, graphs=True):

    # frame offset = ??????
    frame_offset = 0
    frames, threshold_frames = open_video(filename, endingframe)

    frame_data = []

    for frame in threshold_frames:
        frame_data.append(compute_droplet_values_single_frame(frame))

    frame_data = np.array(frame_data)

    # compute velocites
    com_velocity = compute_velocity(frame_data[:, 0])
    com_x_velocity = compute_velocity(frame_data[:, 1])
    tip_velocity = compute_velocity(frame_data[:, 2])
    top_velocity = compute_velocity(frame_data[:, 3])

    # remove first frame
    # compute various weber numbers

    diameters = frame_data[1:, 4]
    lengths = frame_data[1:, 5]

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
        DENSITY * frame_data[1:, 6] * 0.5 *
        com_velocity**2/(surface_area * SURFACE_TENSION))

    weber_number_first_princ_surface_area = 12 * (
        DENSITY * frame_data[1:, 9] * 0.5 *
        com_velocity**2/(frame_data[1:, 10] * SURFACE_TENSION))

    # full frame data contains ...
    # theres a part of me who knows how hacky this looks
    # and there's another larger part that just doesn't care
    a = np.split(frame_data[1:, :], 11, axis=1)
    shape = a[0].shape

    full_frames_data = np.concatenate(
        (*a,
         com_velocity.reshape(shape), com_x_velocity.reshape(shape), tip_velocity.reshape(shape), top_velocity.reshape(shape),
         weber_number_report.reshape(shape),
         weber_number_first_princ.reshape(shape),
         weber_number_first_princ_surface_area.reshape(shape)), axis=1)

    # compute impact frame -> max tip velocity
    pre_impact_frame = np.argmax(full_frames_data[:, 13])

    report_weber_numbers = (full_frames_data[pre_impact_frame, 15],
                            full_frames_data[pre_impact_frame, 16],
                            full_frames_data[pre_impact_frame, 17])
    # this also gives the reported weber numbers

    # compute max spread frame -> give max spread
    max_spread_frame = np.argmax(full_frames_data[:, 4])

    max_spread = full_frames_data[max_spread_frame, 4]
    time_to_max_spread = None

    # There are two maximums in the height
    # the first will occur before impact due to elongation
    # and the second will occur either due to the splash or
    # due to the maximum rosensweig instabilities

    max_height_frame = (
        np.argmax(full_frames_data[max_spread_frame:, 5]) +
        max_spread_frame)

    max_height = full_frames_data[max_height_frame, 5]
    time_to_max_height = None

    # pretty print print summary
    # csv summary

    if graphs:
        animation = display_video_with_com(frames, threshold_frames,
                                           full_frames_data)
        # draw on max spread and weber number points?
        # so this can be saved?
        # save this in good folders?
        graph_velocities_and_length(full_frames_data)

        display_frame_and_surrounding(
            frames, max_spread_frame, title="Max spread frame")

        # display frames of maximum spread?

        plt.show()

    # the frame offset gives the frame in terms of the video frame
    # number rather than the frame number of portion of the
    # video analysed

    # add volume calculations to this output
    # first, and last pre impact
    return (pre_impact_frame + frame_offset, *report_weber_numbers,
            max_spread_frame + frame_offset, max_spread,
            max_height_frame + frame_offset, max_height)
    # print weber number
    # based on final values?
    # or as a function of time?


print(process_side_video(filename, None))
