"""
Open a video and display a specific frame

possibly also save thresholded/cleaned frames etc
"""
import matplotlib.pyplot as plt
import numpy as np
import cv2


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


def open_frame(filename, config, frame_number):
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

        cleaned_frame, convex, contour = clean_frame(threshold_frame, config)
        return (image, threshold_frame, cleaned_frame, convex), contour


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
        return filled_frame, convex_frame, []
    i = np.argmax(object_sizes)

    # print("region area", area)

    cv2.drawContours(filled_frame, cs, i, color=1, thickness=-1)

    convex_hull = cv2.convexHull(cs[i])
    # print("region solidity", solidity)
    # convexImage -- draw on convexI
    cv2.drawContours(convex_frame, [convex_hull], -1,
                     color=1, thickness=-1)
    # this is the most useful as it can be passed back to what I actually
    # calculate in my code

    return filled_frame, convex_frame, cs[i]


def display_frames(frames, contour=None):

    x = []
    y = []
    if contour is not None:
        for a in contour:
            x.append(a[0, 0])
            y.append(a[0, 1])

    x = np.array(x)
    y = np.array(y)

    max_ = len(frames)

    fig, ax = plt.subplots(1, max_, sharey='all', sharex='all')

    for i in range(max_):
        ax[i].imshow(frames[i], cmap='gray')
        ax[i].scatter(x, y, marker='x')

    plt.show()


if __name__ == '__main__':
    filename = input("Please enter filename: ")
    frame_no = int(input("Frame number: "))
    frames, contour = open_frame(
        filename, ConfigurationStephen, frame_no)

    display_frames(frames, contour=contour)

    which_to_save = int(input("Select image to save 0-3: "))

    if which_to_save < 0:
        print("Exiting")
    else:
        out_filename = input("Output filename: ")
        if which_to_save == 0:
            status = cv2.imwrite(out_filename, frames[which_to_save])
        else:
            status = cv2.imwrite(out_filename, frames[which_to_save]*255)
        print("success?", status)
