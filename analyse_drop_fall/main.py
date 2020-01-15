"""
Author: Amelia Cordwell
Description: Analysis and graphing code for the side view of a falling
ferrofluid droplet.
"""

import matplotlib.pyplot as plt
import numpy as np
import cv2

import constants
from display import (
    display_video_with_com, graph_velocities_and_length,
    display_frame_and_surrounding)
from contact_line import (find_equation_of_contact_line,
                          find_contact_width, get_blackout_frame)
from load_data import load_data


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
filename = "/home/amelia/Documents/ferrofluids/dist_-700_crown_C2.avi" # noqa
# filename = "/home/amelia/Documents/ferrofluids/from server/Magnet/Sm_16.5mm/13510_C2/13510_C2.avi"

plt.style.use('ggplot')


def compute_velocity(positions, config):
    positions = np.array(positions)
    # compute velocities attached to the current frame and the frame
    # before, this will mean that there is a velocity associated with
    # all frames except the first one

    dy = (positions[1:] - positions[:-1])
    velocity = dy * config.FRAMES_PER_SECOND

    return velocity


def find_dynamic_max_spread(contact_widths, pre_impact_frame):
    """
    During relaxation into Rosensweig instabilities the diameter
    may grow beyond the maximum spread due to impact phenomena, as
    such the dynamic max spread is not simply found by an arg
    max on the array.

    There are a number of ways of dealing with this, today however
    I will be taking the lazy way out and assuming that max spread
    happens within 40 frames of impact (maybe this should be a
    configurable data point for later on, ugh that's not setup
    yet)

    Later this could be done better, possibly by numerical
    differentiation

    returns: the frame that contains the maximum spread of
    the droplet
    """
    return np.argmax(contact_widths[
            pre_impact_frame:pre_impact_frame+15]) + pre_impact_frame


def get_summary_statistics(full_frames_data, config):
    # sumarise:
    # solidity at max spread

    pass


def post_impact_convex_analysis(reflection_cleaned_frame, config):
    """

    returns:
     - frame with convex version of the hull
     - solidity rating for the droplet in this frame
      (calculated as origional area/convex area)
     - height of the droplet in the frame
    """
    cs, _ = cv2.findContours(reflection_cleaned_frame.astype('uint8'),
                             mode=cv2.RETR_LIST,
                             method=cv2.CHAIN_APPROX_SIMPLE)

    # set up the 'ConvexImage' bit of regionprops.
    convex_frame = np.zeros(
        reflection_cleaned_frame.shape[0:2]).astype('uint8')

    # it is tecnhically possible to get more than one object here
    # if e.g. the droplet splits apart
    object_sizes = np.array([cv2.moments(c)['m00'] for c in cs])

    i = np.argmax(object_sizes)
    c = cs[i]

    area = cv2.contourArea(c)

    convex_hull = cv2.convexHull(c)
    convex_area = cv2.contourArea(convex_hull)
    solidity = area/convex_area

    cv2.drawContours(convex_frame, [convex_hull], -1,
                     color=1, thickness=-1)

    height = (cv2.boundingRect(c)[3] - 1) * config.PIXELS_TO_METERS

    return convex_frame, solidity, height


def process_side_video(filename, config, graphs=True):
    (frame_array, threshold_frame_array,
     cleaned_frame_array, convex_frame_array, droplet_contours,
     convex_frame_data, frame_data, frame_offset) = load_data(
        filename, config)

    # compute velocities
    com_velocity = compute_velocity(convex_frame_data[:, 0], config)
    com_x_velocity = compute_velocity(convex_frame_data[:, 1], config)
    tip_velocity = compute_velocity(convex_frame_data[:, 2], config)
    top_velocity = compute_velocity(convex_frame_data[:, 3], config)

    # remove first frame
    # compute various weber numbers

    # non convex for this as this is the largest and
    # shouldn't be affected by reflections
    diameters = convex_frame_data[1:, 4]
    lengths = convex_frame_data[1:, 5]

    # TODO(amelia): Clean this mess up
    # although that might mean changing the way the calculation works
    surface_area = np.pi * diameters/2 * (
        lengths * ((np.arcsin(np.sqrt(1 - diameters**2/lengths))) /
                   (np.sqrt(1 - diameters**2/lengths)))
        + diameters)

    # Only care about weber numbers for convex frame, as falling droplets
    # are convex, this means that there are incorrect after falling
    weber_number_report = (np.pi * config.DENSITY * lengths * diameters**2 *
                           com_velocity**2 /
                           (surface_area * config.SURFACE_TENSION))

    weber_number_first_princ = 12 * (
        config.DENSITY * convex_frame_data[1:, 6] * 0.5 *
        com_velocity**2/(surface_area * config.SURFACE_TENSION))

    weber_number_first_princ_surface_area = 12 * (
        config.DENSITY * convex_frame_data[1:, 9] * 0.5 *
        com_velocity**2/(convex_frame_data[1:, 10] * config.SURFACE_TENSION))

    # full frame data contains ...
    # theres a part of me who knows how hacky this looks
    # and there's another larger part that just doesn't care

    full_frames_data = {
        'frame_data': frame_data,
        'convex_frame_data': convex_frame_data,
        'contours': droplet_contours,
        'weber_numbers': {
            'report': weber_number_report,
            'first_princ': weber_number_first_princ,
            'first_princ_conical': weber_number_first_princ_surface_area
        },
        'velocities': {
            'com': com_velocity, 'comx': com_x_velocity,
            'top': top_velocity,
            'tip': tip_velocity,
        }
    }

    # compute impact frame -> max tip velocity
    pre_impact_frame = np.argmax(full_frames_data['velocities']['tip'])
    full_frames_data['pre_impact_frame'] = pre_impact_frame

    report_weber_numbers = (
        full_frames_data['weber_numbers']['report'][pre_impact_frame],
        full_frames_data['weber_numbers']['first_princ'][pre_impact_frame],
        full_frames_data['weber_numbers'][
            'first_princ_conical'][pre_impact_frame])
    # this also gives the reported weber numbers

    # compute other stuff
    # compute contact line and contact line dynamics

    # create numpy array of contact line dynamics ()
    # for all of the frames
    line, contact_points_x, contact_points_y = find_equation_of_contact_line(
        droplet_contours, pre_impact_frame, config, return_points=True)

    contact_widths = []
    for frame in cleaned_frame_array:
        contact_widths.append(find_contact_width(frame, line, config))

    full_frames_data['contact_width'] = (
        np.array(contact_widths) * config.PIXELS_TO_METERS)

    blackout_frame = get_blackout_frame(frame_array[0].shape, line, config)

    # remove reflection and compute heights
    reflection_cleaned_frames = cleaned_frame_array & blackout_frame

    reflection_cleaned_convex_frames = []
    reflection_cleaned_heights = []
    solidity = []

    for frame in reflection_cleaned_frames:
        f, solid, height = post_impact_convex_analysis(frame, config)
        reflection_cleaned_convex_frames.append(f)
        reflection_cleaned_heights.append(height)
        solidity.append(solid)

    full_frames_data['solidity'] = solidity
    full_frames_data[
        'reflect_cleaned_heights'] = reflection_cleaned_heights

    # MAX SPREAD ANALYSIS
    # compute max spread frame -> give max spread
    max_spread_frame = find_dynamic_max_spread(contact_widths,
                                               pre_impact_frame)
    max_spread = convex_frame_data[max_spread_frame, 4]

    full_frames_data['max_spread_frame'] = max_spread_frame

    # summary = get_summary_statistics(full_frames_data)

    # time from last pre impact frame
    time_to_max_width = (
        max_spread_frame - pre_impact_frame)/config.FRAMES_PER_SECOND

    # There are two maximums in the height
    # the first will occur before impact due to elongation
    # and the second will occur either due to the splash or
    # due to the maximum rosensweig instabilities

    max_height_frame = (
        np.argmax(convex_frame_data[max_spread_frame:, 5]) +
        max_spread_frame)

    max_height = convex_frame_data[max_height_frame, 5]
    time_to_max_height = (
        max_height_frame - pre_impact_frame)/config.FRAMES_PER_SECOND

    if graphs:
        #animation = display_video_with_com(
        #    (frame_array, cleaned_frame_array,
        #     convex_frame_array, reflection_cleaned_frames,
        #     reflection_cleaned_convex_frames),
        #    full_frames_data, config, line=line)
        # draw on max spread and weber number points?
        # so this can be saved?
        # save this in good folders?
        graph_velocities_and_length(full_frames_data, config)

        display_frame_and_surrounding(
            frame_array, max_spread_frame, config,
            title="Max spread frame")

        # display frames of maximum spread?

        plt.show()

    # the frame offset gives the frame in terms of the video frame
    # number rather than the frame number of portion of the
    # video analysed

    start_volume = convex_frame_data[0, 9]  # using conical approximation
    pre_impact_volume = convex_frame_data[pre_impact_frame, 9]

    return (pre_impact_frame + frame_offset, *report_weber_numbers, # noqatop
            max_spread_frame + frame_offset, time_to_max_spread, max_spread,
            max_height_frame + frame_offset, time_to_max_height, max_height,
            start_volume, pre_impact_volume, frame_offset)


if __name__ == '__main__':
    print("Pre impact frame, weber number report, weber number first "
          "principles, weber number first principles cone approximation, "
          "max spread frame, time from pre impact frame to max spread frame, "
          "max spread width (m), max height frame, time to max height,"
          " max height, first calculated volume, volume calculated on the pre"
          " impact frame")
    print(process_side_video(filename, constants.ConfigurationDecember7))
