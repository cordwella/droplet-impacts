"""
Functions for contact line analysis and post processing
"""

import numpy as np
import cv2


def find_equation_of_contact_line(contours, pre_impact_frame,
                                  config,
                                  return_points=False):
    """
    Find the best fit contact line by calculating the contact points line for
    frames 2 - 7 post impact and taking the line of best fit between them

    Slight disagreements shouldn't matter as the overall uncertainty is
    a pixel, and that shouldn't change anything

    optionally will also display the whole contact line and each of the contact
    points in different colours/shapes to fix things

    inputs:
        - contours see main.py
        - pre impact frame : the index (wrt full_frames_data) of the frame
        immediately before impact
    outputs:
        - numpy poly1d defining the line
    """

    frames_to_use = range(pre_impact_frame + config.CONTACT_LINE_FIRST_FRAME,
                          pre_impact_frame + config.CONTACT_LINE_LAST_FRAME, 1)

    contact_points_x = []
    contact_points_y = []

    for frame in frames_to_use:
        try:
            width, left, right = find_contact_points(contours[frame], config)
        except IndexError:
            break
        if width:
            contact_points_x.append(left[0])
            contact_points_x.append(right[0])

            contact_points_y.append(left[1])
            contact_points_y.append(left[1])

    if len(contact_points_x) == 0:
        z = None
    else:
        z = np.poly1d(np.polyfit(contact_points_x, contact_points_y, 1))

    if return_points:
        return z, contact_points_x, contact_points_y

    return z


def find_contact_points(contour, config):
    """
    find contact points and contact width in pixels
    based on a contour, and performing pixel by pixel operations only

    only works for contact angles less than 90 degrees, accuraccy is
    on the pixel scale, sub pixel optimization not possible with
    thresholded images

    algorithm description to come (one exists in my notebook)

    input:
        - contour
        - config file
    output:
        - contact width (in pixels)
        - left contact point
        - right contact point
    """
    left_contact_points = None
    right_contact_points = None

    rect = cv2.boundingRect(contour)
    # rect is x start, y start and then offsets to fill the whole rectangle
    comx = rect[0] + 0.5 * rect[2]

    num_points = len(contour)

    for i in range(len(contour) + 4):
        # i = i % len(contour)
        previous_point = contour[(i - 1) % num_points][0]
        central_point = contour[i % num_points][0]
        next_point = contour[(i + 1) % num_points][0]
        next_next_point = contour[(i + 2) % num_points][0]

        # check if they are all left/right of the comx

        # contours are output counter clockwise, so some assumptions
        # can be made based on this

        if central_point[0] + 20 < comx:
            # left contact point

            # two cases

            # 3 point case and 4 point case
            # definition in lab book
            # should be added to some notes on the latex doc later
            # under software descriptions
            # and in the lab note book
            if (previous_point[1] < central_point[1] and
                    central_point[1] < next_point[1]):
                if central_point[0] == next_point[0]:
                    # 4 point case
                    if (previous_point[0] < central_point[0] and
                            next_next_point[0] < central_point[0]):
                        # print("left 4")
                        actual_center = (
                            central_point[0],
                            0.5 * (central_point[1] + next_point[1]))

                        if left_contact_points:
                            if actual_center[1] > left_contact_points[0][1]:
                                # check which one is lower
                                # print("confusion left, setting lower yvalue")

                                left_contact_points = [
                                    previous_point, actual_center,
                                    next_next_point]
                        else:
                            left_contact_points = [
                                previous_point, actual_center, next_point]

                elif (previous_point[0] < central_point[0] and
                        next_point[0] < central_point[0]):
                    # print("left 3")

                    if left_contact_points:
                        if central_point[1] > left_contact_points[0][1]:
                            # check which one is lower
                            # print("confusion left, setting lower yvalue")

                            left_contact_points = [
                                previous_point, central_point, next_point]
                    else:
                        left_contact_points = [
                            previous_point, central_point, next_point]

        elif central_point[0] - 20 > comx:
            # if they are all right of the comx
            if (previous_point[1] > central_point[1] and
                    central_point[1] > next_point[1]):
                if central_point[0] == next_point[0]:
                    # 4 point case
                    if (previous_point[0] > central_point[0] and
                            next_next_point[0] > central_point[0]):
                        # print("Found right 4")
                        actual_center = (
                            central_point[0],
                            0.5 * (central_point[1] + next_point[1]))

                        if right_contact_points:
                            if actual_center[1] > right_contact_points[0][1]:
                                # check which one is lower
                                right_contact_points = [
                                    previous_point, actual_center,
                                    next_next_point]
                        else:
                            right_contact_points = [
                                previous_point, actual_center, next_point]

                elif (previous_point[0] > central_point[0] and
                      next_point[0] > central_point[0]):
                    # print("Found right 3")

                    if right_contact_points:

                        if central_point[1] > right_contact_points[0][1]:
                            # check which one is lower
                            # print("confusion right, setting lower yvalue")

                            right_contact_points = [
                                previous_point, central_point, next_point]
                    else:
                        right_contact_points = [
                            previous_point, central_point, next_point]

    if not left_contact_points or not right_contact_points:
        print("Unable to find contact points with angle > 90")
        return None, None, None

    contact_width = np.sqrt(
        (left_contact_points[1][0] - right_contact_points[1][0])**2 +
        (left_contact_points[1][1] - right_contact_points[1][1])**2)
    contact_width = contact_width * config.PIXELS_TO_METERS

    # NOTE(amelia): I would also like to return contact angle
    # however this would likely require the modelling of the whole
    # drop due to pixelization issues otherwise

    return contact_width, left_contact_points[1], right_contact_points[1]


def find_contact_width(threshold_frame, line, config):
    """
    Find the distance (in pixels) across the contact line of the droplet
    this doesn't require a contact angle g
    inputs:
        - cleaned thresholded frame
        - line defining numpy equation of the contact line, should be a
          numpy polyval
        - config
    output:
        - width of pixels across 'line' in pixels
    """

    if config.GET_MAX_CONTACT is False:
        return _find_contact_width(threshold_frame, line, config)

    coeffs = line.c

    line_above = np.poly1d([coeffs[0], coeffs[1] + 2])
    line_below = np.poly1d([coeffs[0], coeffs[1] - 1])

    widths = [_find_contact_width(threshold_frame, l, config)
              for l in (line_above, line, line_below)]
    return max(widths)


def _find_contact_width(threshold_frame, line, config):
    frame_width = threshold_frame.shape[1]

    # defining the contact line
    x_values = np.linspace(0, frame_width - 1, 3000)
    # standard int rounding always rounds down
    y_values = (line(x_values) + 0.5).astype(int, copy=False)
    x_values = x_values.astype(int, copy=False)

    # find nonzero points on threshold frame, and external parts of
    # these

    pixels_along_line = threshold_frame[y_values, x_values]
    if not pixels_along_line.nonzero()[0].any():
        return 0

    id_left_contact = pixels_along_line.nonzero()[0][0]
    id_right_contact = pixels_along_line.nonzero()[0][-1]

    contact_width = np.sqrt(
        (x_values[id_left_contact] - x_values[id_right_contact])**2 +
        (y_values[id_left_contact] - y_values[id_right_contact])**2)

    # Add one to this number as the calculated width is between the
    # center of each of the pixels and all other calculations calculate it
    # from the ends of the pixels
    return contact_width


def get_blackout_frame(shape, line, config):
    """
    Clean the reflection from a thresholded frame

    inputs: threshold_frame (obs)
    line is a numpy polyl1d object defining the line of contact/reflection

    returns threshold_frame (modified in place), with the area
    below the reflection line blacked out
    """
    # remove reflective area from the thresholded frames
    frame_width = shape[0]
    blackout_frame = np.zeros(shape[0:2]).astype('uint8')

    polygon_points = [[0, 0], [0, line(0)], [frame_width, line(frame_width)],
                      [frame_width, 0]]

    cv2.fillConvexPoly(
        blackout_frame, np.array([polygon_points], np.int32), 1)

    return blackout_frame
