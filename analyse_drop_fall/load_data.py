import cv2
import numpy as np


def load_data(filename, config, load_offset=0):
    frame_array = []
    threshold_frame_array = []
    cleaned_frame_array = []
    convex_frame_array = []
    contour_array = []
    frame_data_array = []
    convex_frame_data = []

    vidcap = cv2.VideoCapture(filename)

    count = 0
    success = True
    calculated_starting_frame = False
    background_image = None

    success, image = vidcap.read()

    print(success, image)

    while load_offset > 0:
        success, image = vidcap.read()
        load_offset = load_offset - 1


    while success and len(frame_array) <= config.MAXIMUM_FRAME_NO:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            break

        # transform image to only get the first color value
        image = image[:, :, 0]  # black and white single channel image

        if config.CROP_DIMENSIONS:
            CROP_DIMENSIONS = config.CROP_DIMENSIONS
            image = image[CROP_DIMENSIONS[0]:CROP_DIMENSIONS[2],
                          CROP_DIMENSIONS[1]:CROP_DIMENSIONS[3]]

        if background_image is None:
            background_image = image

        if config.SUBTRACT_BACKGROUND:
            if config.BACKGROUND_SUBTRACT_MODE == 'MATCH':
                # for some (read stephens) images there is significant
                # black backgrounds in the same area as the black ferrofluid
                # as such doing a standard subtraction itsn't great
                # this is the best solution I have for matching them
                # together
                image[abs(background_image/2 - image/2) <
                      config.BACKGROUND_MATCH_THRESHOLD] = 255
            else:
                # standard background subtraction
                # divide by two as images are non negative append otherwise
                # there are weird wrap around effects
                image = 255 - abs(image/2 - background_image/2)

        threshold_image = (image < config.THRESHOLD_LEVEL).astype(int)

        if (not calculated_starting_frame and threshold_image.any()
                and not threshold_image[0, :].any()):
            # there is a droplet in the frame and it is full in the frame
            filled_frame, convex_frame, contour = clean_frame(
                threshold_image, config)

            if len(contour) != 0 and cv2.contourArea(contour) >= config.MINIMUM_DROPLET_AREA:
                calculated_starting_frame = count

        if calculated_starting_frame:
            # check for emptiness in the threshold image
            filled_frame, convex_frame, contour = clean_frame(
                threshold_image, config)

            if len(contour) == 0 and len(frame_array) <= 1:
                frame_array = []
                threshold_frame_array = []
                convex_frame_array = []
                contour_array = []
                convex_frame_data = []
                frame_data_array = []
                calculated_starting_frame = None
            elif len(contour) == 0:
                vidcap.release()
                return (frame_array, threshold_frame_array,
                        cleaned_frame_array, convex_frame_array, contour_array,
                        np.array(convex_frame_data), np.array(frame_data_array),
                        calculated_starting_frame)
            else:
                frame_array.append(image)
                threshold_frame_array.append(threshold_image)

                starty = (cv2.boundingRect(contour)[1]
                          + cv2.boundingRect(contour)[3] - 1)

                cleaned_frame_array.append(filled_frame)
                convex_frame_array.append(convex_frame)
                contour_array.append(contour)

                # generic parameters (for convex frame)
                # generic parameters to be trusted for droplet falling
                # frames only, and not for post/during impact

                convex_frame_data.append(compute_droplet_values_single_frame(
                    convex_frame, starty, config))

                frame_data_array.append(compute_droplet_values_single_frame(
                    filled_frame, starty, config))

        count += 1

    print(count)

    vidcap.release()
    return (frame_array, threshold_frame_array,
            cleaned_frame_array, convex_frame_array, contour_array,
            np.array(convex_frame_data), np.array(frame_data_array),
            calculated_starting_frame)


def clean_frame(threshold_frame, config):
    """ Clean the frame to have the largest object only using open cv functions

    With thanks to stack overflow:
    https://stackoverflow.com/questions/9056646/python-opencv-find-black-areas-in-a-binary-image

    See also:
    https://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html
    """

    if config.CLEAN_FRAME:

        cs, _ = cv2.findContours(threshold_frame.astype('uint8'),
                                 mode=cv2.RETR_LIST,
                                 method=cv2.CHAIN_APPROX_SIMPLE)
        # set up the 'ConvexImage' bit of regionprops.
        filled_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')
        convex_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')

        # for each contour c in cs:
        # will demonstrate with cs[0] but you could use a loop.
        object_sizes = np.array([cv2.moments(c)['m00'] for c in cs])

        if not object_sizes.any():
            return filled_frame, convex_frame, []
        i = np.argmax(object_sizes)
        c = cs[i]
        # calculate some things useful later:
        # m = cv2.moments(c)

        # ** regionprops **
        # area = m['m00']
        # print("region area", area)

        cv2.drawContours(filled_frame, cs, i, color=1, thickness=-1)

        # this should only come up when the droplet is falling
        # not when it's on the ground at which point it shouldn't be
        # convex
        # CONVEX HULL stuff
        # convex hull vertices
        convex_hull = cv2.convexHull(c)
        # convex_area = cv2.contourArea(convex_hull)
        # Solidity := Area/ConvexArea
        # solidity = area/convex_area
        # print("region solidity", solidity)
        # convexImage -- draw on convexI
        cv2.drawContours(convex_frame, [convex_hull], -1,
                         color=1, thickness=-1)
        # this is the most useful as it can be passed back to what I actually
        # calculate in my code

        return filled_frame, convex_frame, c
    else:
        # we dont want to get rid of smaller droplets
        cs, _ = cv2.findContours(threshold_frame.astype('uint8'),
                                 mode=cv2.RETR_LIST,
                                 method=cv2.CHAIN_APPROX_SIMPLE)
        # set up the 'ConvexImage' bit of regionprops.
        filled_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')
        convex_frame = np.zeros(threshold_frame.shape[0:2]).astype('uint8')

        # for each contour c in cs:
        # will demonstrate with cs[0] but you could use a loop.
        object_sizes = np.array([cv2.moments(c)['m00'] for c in cs])

        if not object_sizes.any():
            return filled_frame, convex_frame, []
        i = np.argmax(object_sizes)
        c = cs[i]
        # calculate some things useful later:
        # m = cv2.moments(c)

        convex_hull = cv2.convexHull(c)
        # convex_area = cv2.contourArea(convex_hull)
        # Solidity := Area/ConvexArea
        # solidity = area/convex_area
        # print("region solidity", solidity)
        # convexImage -- draw on convexI
        cv2.drawContours(convex_frame, [convex_hull], -1,
                         color=1, thickness=-1)
        # this is the most useful as it can be passed back to what I actually
        # calculate in my code

        # were not going to actually return the filled frame
        # just the original thresholded frame and the convex hull
        # makes life easier for Alex's code
        return threshold_frame, convex_frame, c


def compute_droplet_values_single_frame(threshold_frame, starty, config):
    # NOTE(amelia); there is probably a bunch of this that could be optimized
    # by using the frame contours rather than just this however frankly
    # I can't be bothered, and it wouldn't give better values
    # (although it could deal with smoothing and smooth out the jitters)

    # find first y coordinate from the frame
    y_coord = starty

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
        # measure pixel to pixel distance
        if np.count_nonzero(line) == 0:
            break

        width = len(line) - np.argmax(line) - np.argmax(line[::-1])	- 1
        # width = np.count_nonzero(line) - 1
        #if width == -1:
            # no longer counting the actual size
        #    break
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

    # full length of the droplet
    length = starty - y_coord - 1

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

    vertical_com = vertical_com * config.PIXELS_TO_METERS
    horizontal_com = horizontal_com * config.PIXELS_TO_METERS
    top_y_coordinate = starty * config.PIXELS_TO_METERS
    bottom_y_coord = y_coord * config.PIXELS_TO_METERS
    max_width = max_width * config.PIXELS_TO_METERS
    length = length * config.PIXELS_TO_METERS

    # cylindrical volume approximation
    volume = volume * config.PIXELS_TO_METERS**3
    volume_ellipse = volume_ellipse * config.PIXELS_TO_METERS**3
    surface_area_ellipse = surface_area_ellipse

    volume_cone = volume_cone * config.PIXELS_TO_METERS**3
    surface_area_cone = surface_area_cone * config.PIXELS_TO_METERS**2

    return (vertical_com, horizontal_com, top_y_coordinate, bottom_y_coord,
            max_width, length,
            volume, volume_ellipse, surface_area_ellipse,
            volume_cone, surface_area_cone)
