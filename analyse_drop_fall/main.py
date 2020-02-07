"""
Author: Amelia Cordwell
Description: Analysis and graphing code for the side view of a falling
ferrofluid droplet.
"""

import pickle
import os

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


# TODO(amelia): test the surface area calculations against known 'perfect'
# shapes and generate videos
# build checking for when the drop is falling DONE
# compute maximum spread and frame number for maximum spread DONE
# shove up a display of the maximum spread frame not yet
# determine cropping dimensions and bottom dimension for thing done, sort of
#   this is currently determined by
# or do I determine this by position when
# filename = "/home/amelia/Documents/ferrofluids/p01c2_C2.avi"

# plt.style.use('ggplot')


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


def summarise_data(full_frames_data, config):
    """
    Return a one line summary of the data useful for processing with
    different scripts or in a spreadsheeting program

    returns
    at start:
        - volume
        - surface area
        - velocity
    at pre impact:
        - weber numbers pre impact
        - surface area
        - CoM velocity
        - volume
        - solidity
        - frame number
    at max spread:
        - max spread
        - solidity
        - height
        - time from pre impact
        - frame number
    at max diameter
        - same as maximum spread


    various times (not yet):
        - report time from pre impact frame, height, contact width,
          solidity, frame no 200
        - contact width > max spread again
        - contact width minimum
        - max rosensweig height
        - final frame
    """

    """ 0 frame, 0 time, 0 length, 0 contact width, 0 width, 0 solidity, 0 volume,
       pre frame, pre time, pre length, pre contact width, pre width, pre solidity, pre volume
       pre com v, pre weber,
       max spread frame, spread time, spread height, spread contact width, spread max width, spread solidity,
     """

    first_frame = summarise_frame_data(full_frames_data, 0, config)
    first_frame.append(full_frames_data['convex_frame_data'][0, 9])  # volume
    # conically calculated surface area
    first_frame.append(full_frames_data['convex_frame_data'][0, 10])

    # which ever number gives standard volume
    # TODO

    pre_impact = summarise_frame_data(
        full_frames_data, full_frames_data['pre_impact_frame'], config)
    pre_impact.append(
        full_frames_data['frame_data'][full_frames_data['pre_impact_frame'],
                                       9])  # volume
    pre_impact.append(
        full_frames_data['frame_data'][full_frames_data['pre_impact_frame'],
                                       10])  # surface area

    pre_impact.append(
        full_frames_data['velocities']['com'][
            full_frames_data['pre_impact_frame']])
    pre_impact.append(
        full_frames_data['velocities']['tip'][
            full_frames_data['pre_impact_frame']])
    print('Pre impact velocity', full_frames_data['velocities']['com'][
        full_frames_data['pre_impact_frame']])

    # standard weber number
    pre_impact.append(
        full_frames_data['weber_numbers']['first_princ_conical'][
            full_frames_data['pre_impact_frame']])
    #
    pre_impact.append(
        full_frames_data['weber_numbers']['fixed_volume'][
            full_frames_data['pre_impact_frame']])

    pre_impact.append(
        full_frames_data['weber_numbers']['tip'][
            full_frames_data['pre_impact_frame']])

    # pre impact . append VELOCITY and WEBER NUMBERs
    # NOTE which weber number is the best ???
    # first princ conical -> but also ask

    max_spread = summarise_frame_data(
        full_frames_data, full_frames_data['max_spread_frame'], config)
    max_diameter = summarise_frame_data(
        full_frames_data, full_frames_data['max_diameter_frame'], config)

    summary = first_frame + pre_impact + max_spread + max_diameter

    # TODO: In future at this I could also look at
    # specific interesting points, ie max height etc
    # however this depends on the regime that the droplet
    # is in and as such without further more qualitative study
    # i cannot do this

    return summary


def summarise_frame_data(full_frames_data, frame_number, config,):
    """
    return for specified frame
    time, since pre impact frame, height, contact width, solidity
    """
    time = (frame_number -
            full_frames_data['pre_impact_frame'])/config.FRAMES_PER_SECOND

    height = full_frames_data['frame_data'][frame_number, 4]
    contact_width = full_frames_data['contact_width'][frame_number]
    max_width = full_frames_data['frame_data'][frame_number, 5]
    solidity = full_frames_data['solidity'][frame_number]

    return [frame_number, time, height, contact_width, max_width, solidity]


def process_side_video(filename, config, graphs=True, save_filename=None):
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

    # Only care about weber numbers for convex frame, as falling droplets
    # are convex, this means that there are incorrect after falling

    weber_number_first_princ_surface_area = 12 * (
        config.DENSITY * convex_frame_data[1:, 9] * 0.5 *
        com_velocity**2/(convex_frame_data[1:, 10] * config.SURFACE_TENSION))

    weber_number_fixed_volume = 12 * (
        config.DENSITY * convex_frame_data[0, 9] * 0.5 *
        com_velocity**2/(convex_frame_data[1:, 10] * config.SURFACE_TENSION))

    weber_number_tip = 12 * (
        config.DENSITY * convex_frame_data[0, 9] * 0.5 *
        tip_velocity**2/(convex_frame_data[1:, 10] * config.SURFACE_TENSION))

    # full frame data contains ...
    # theres a part of me who knows how hacky this looks
    # and there's another larger part that just doesn't care

    full_frames_data = {
        'frame_data': frame_data,
        'convex_frame_data': convex_frame_data,
        'contours': droplet_contours,
        'weber_numbers': {
            'first_princ_conical': weber_number_first_princ_surface_area,
            'fixed_volume': weber_number_fixed_volume,
            'tip': weber_number_tip,
        },
        'velocities': {
            'com': com_velocity, 'comx': com_x_velocity,
            'top': top_velocity,
            'tip': tip_velocity,
        }
    }

    # compute impact frame -> max tip velocity
    # get last maximum value
    # TODO(amelia): document this properly
    pre_impact_frame = np.argmax(full_frames_data['velocities']['tip'])
    b = full_frames_data['velocities']['tip'][::-1]
    pre_impact_frame = len(b) - np.argmax(b) - 1

    # this also gives the reported weber numbers

    # compute other stuff
    # compute contact line and contact line dynamics

    # create numpy array of contact line dynamics ()
    # for all of the frames
    line, contact_points_x, contact_points_y = find_equation_of_contact_line(
        droplet_contours, pre_impact_frame, config, return_points=True)

    contact_widths = []
    if line is None:
        # make line instead the bottom of the frame
        line = np.poly1d([0, cleaned_frame_array[0].shape[0] - 1])
    full_frames_data['contact_line'] = line
    for frame in cleaned_frame_array:
        contact_widths.append(find_contact_width(frame, line, config))

    full_frames_data['contact_width'] = (
        np.array(contact_widths) * config.PIXELS_TO_METERS)

    blackout_frame = get_blackout_frame(frame_array[0].shape, line, config)

    # check if the pre contact tip position is within blackout
    # if it is then check the previous one
    # and so forth until it finds one it's not
    # pick that frame as the pre impact frame

    center = int(frame_array[0].shape[1]/2)
    while (blackout_frame[int(convex_frame_data[pre_impact_frame + 1, 2] /
                              config.PIXELS_TO_METERS), center] == 0):
        pre_impact_frame = pre_impact_frame - 1

    full_frames_data['pre_impact_frame'] = pre_impact_frame

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

    max_diameter_frame = find_dynamic_max_spread(diameters,
                                                 pre_impact_frame)

    full_frames_data['max_spread_frame'] = max_spread_frame
    full_frames_data['max_diameter_frame'] = max_diameter_frame

    summary = summarise_data(full_frames_data, config)

    # There are two maximums in the height
    # the first will occur before impact due to elongation
    # and the second will occur either due to the splash or
    # due to the maximum rosensweig instabilities

    if graphs:
        animation = display_video_with_com(
            (frame_array, cleaned_frame_array,
             convex_frame_array, reflection_cleaned_frames,
             reflection_cleaned_convex_frames),
            full_frames_data, config, line=line)

        display_frame_and_surrounding(
            frame_array, max_spread_frame, config,
            title="Maximum spread frame")

        display_frame_and_surrounding(
            frame_array, max_diameter_frame, config,
            title="Maximum Diameter Frame")

        graph_velocities_and_length(full_frames_data, config)

        plt.show()

    if save_filename:
        if not os.path.exists(os.path.dirname(save_filename)):
            os.makedirs(os.path.dirname(save_filename))
        with open(save_filename, "wb") as f:
            pickle.dump(full_frames_data, f)

    return (summary, frame_offset)


if __name__ == '__main__':
    print(process_side_video("/home/amelia/Documents/ferrofluids/big data/videos/amelia/9-dec/SM_20mm_sd/dist_-700_crown_C2/dist_-700_crown_C2.avi", constants.ConfigurationDecember7))
