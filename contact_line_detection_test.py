"""
Test the contact line detection algorithm


Current status: working properly for a single frame
haven't yet decided the best way to use for all frames/combine for
all of the frames

Will probably be based on doing a polyfit across all of the values

Author: Amelia Cordwell
"""

import cv2
import numpy as np

import matplotlib.pyplot as plt


class ConfigurationStephen:
    # Configurable constants
    THRESHOLD_LEVEL = 35  # thresholding the image to pick up the drop
    CROP_DIMENSIONS = (0, 0, 665, 350)
    # crop the image to these dimensions
    # (ystart, xstart, yend, xend)
    DENSITY = 1210       # The density of the ferrofluid (kg/m^3)
    SURFACE_TENSION = 0.026  # The surface tension of the ferrofluid
    PIXELS_TO_MM = 0.028563817267384453
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)
    # Conversion from pixels to meters
    # based on the slide in use
    FRAMES_PER_SECOND = 2000

    SUBTRACT_BACKGROUND = False

    # maxiumum number of frames to consider
    MAXIMUM_FRAME_NO = 300

    # in pixels
    MINIMUM_DROPLET_AREA = 60


def find_contact_line(threshold_frame, contour, comx, config):
    left_contact_points = None
    right_contact_points = None

    # comx = frame_data[1]/config.PIXELS_TO_METERS

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
        if left_contact_points:
            print("left", left_contact_points)
        if right_contact_points:
            print("right", right_contact_points)
        return None, None, None

    print("Left", left_contact_points)
    print("Right", right_contact_points)

    contact_width = np.sqrt(
        (left_contact_points[1][0] - right_contact_points[1][0])**2 +
        (left_contact_points[1][1] - right_contact_points[1][1])**2)
    print("contact pixel width", contact_width)
    contact_width = contact_width * config.PIXELS_TO_METERS

    # later on I would also like to return contact angle

    # NOTE(amelia): This works sometimes, but not super well, certain
    # frames could be picked to find this for (ie 5 frames after initial
    # impact), which would then define the line

    return contact_width, left_contact_points[1], right_contact_points[1]


def open_frame(filename, frame_number, config):
    threshold_frame = []

    vidcap = cv2.VideoCapture(filename)

    count = -1
    success = True

    while success and count <= config.MAXIMUM_FRAME_NO:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            break

        count += 1

        if count != frame_number:
            continue

        # transform image to only get the first color value
        image = image[:, :, 0]  # black and white single channel image

        # If a background image has been taken this shouldn't
        # be nessecary

        # perform image testing
        if config.CROP_DIMENSIONS:
            CROP_DIMENSIONS = config.CROP_DIMENSIONS
            image = image[CROP_DIMENSIONS[0]:CROP_DIMENSIONS[2],
                          CROP_DIMENSIONS[1]:CROP_DIMENSIONS[3]]

        threshold_frame = (image < config.THRESHOLD_LEVEL).astype(int)

        cleaned_frame, convex, c = clean_frame(threshold_frame, config)
        return image, threshold_frame, cleaned_frame, convex, c


def clean_frame(threshold_frame, config):
    """ Clean the frame to have the largest object only using open cv functions

    With thanks to stack overflow:
    https://stackoverflow.com/questions/9056646/python-opencv-find-black-areas-in-a-binary-image

    See also:
    https://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html
    """

    cs, _ = cv2.findContours(threshold_frame.astype('uint8'),
                             mode=cv2.RETR_LIST,
                             method=cv2.CHAIN_APPROX_SIMPLE)
    # set up the 'ConvexImage' bit of regionprops.
    filled_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')
    convex_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')

    object_sizes = np.array([cv2.moments(c)['m00'] for c in cs])

    if not object_sizes.any():
        return [], []
    i = np.argmax(object_sizes)

    cv2.drawContours(filled_frame, cs, i, color=1, thickness=-1)

    convex_hull = cv2.convexHull(cs[i])
    # print("region solidity", solidity)
    # convexImage -- draw on convexI
    cv2.drawContours(convex_frame, [convex_hull], -1,
                     color=1, thickness=-1)
    # this is the most useful as it can be passed back to what I actually
    # calculate in my code

    return filled_frame, convex_frame, cs[i]


def test_contact_line_detection(filename, frame, config):
    image, threshold_frame, cleaned_frame, convex, contour = open_frame(
        filename, frame, config)

    # compute center of mass in x direction
    # from the contour
    # actually I don't really care too much so Im just going to take the
    # exact center
    rect = cv2.boundingRect(contour)
    # rect is x start, y start and then offsets to fill the whole rectangle
    comx = rect[0] + 0.5 * rect[2]
    # comy = rect[1] + 0.5 * rect[3]

    width, left, right = find_contact_line(
        threshold_frame, contour, comx, config)

    if not width:
        print("Contact line not found")

        frames = image, cleaned_frame
        max_ = 2

        fig, ax = plt.subplots(1, max_, sharey='all', sharex='all')

        for i in range(max_):
            ax[i].imshow(frames[i], cmap='gray')

        plt.show()
        return

    # calculate line of best fit through the points

    x = np.array([left[0], right[0]])
    y = np.array([left[1], right[1]])

    z = np.polyfit(x, y, 1)

    print(z)

    xp = np.linspace(0, config.CROP_DIMENSIONS[3], 100)
    p = np.poly1d(z)

    frames = image, cleaned_frame
    max_ = 2

    fig, ax = plt.subplots(1, max_, sharey='all', sharex='all')

    for i in range(max_):
        ax[i].imshow(frames[i], cmap='gray')
        ax[i].scatter(x, y, marker='x')
        ax[i].plot(xp, p(xp))

    plt.show()

    # display whole frame

    # with contact line on top of it

    # pass it into the contact line computation

    # display points and contact line


if __name__ == '__main__':
    test_contact_line_detection(
        '/home/amelia/Documents/ferrofluids/from server/Magnet/Sm_16.5mm/14150(2)_C2/14150(2)_C2.avi',
        int(input("frame:")), ConfigurationStephen)
