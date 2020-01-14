"""
Open a video and display a specific frame

possibly also save thresholded/cleaned frames etc
"""
import matplotlib.pyplot as plt
import numpy as np
import cv2


class ConfigurationStephen:
    # Configurable constants
    THRESHOLD_LEVEL = 250  # thresholding the image to pick up the drop
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


BACKGROUND_FRAME_NO = 0


def open_frame(filename, config, frame_number):
    vidcap = cv2.VideoCapture(filename)

    count = -1
    success = True

    background_image = None

    while success and count <= config.MAXIMUM_FRAME_NO:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            break

        count += 1

        if count == BACKGROUND_FRAME_NO:
            background_image = image[:, :, 0]

        if count != frame_number:
            continue

        # transform image to only get the first color value
        image = image[:, :, 0]  # black and white single channel image

        # If a background image has been taken this shouldn't
        # be nessecary

        # perform image testing

        subtracted_image = 255 - abs(image/2 - background_image/2)

        image2 = image.copy()
        image2[abs(background_image/2 - image2/2) < 3] = 255

        return (
            image, subtracted_image, background_image,
            (subtracted_image < 245).astype(int),
            (image < 30).astype(int),
            image2,
            (image2 < 50).astype(int))


def display_frames(frames):
    max_ = len(frames)

    fig, ax = plt.subplots(1, max_, sharey='all', sharex='all')
    plt.tight_layout()

    for i in range(max_):
        ax[i].imshow(frames[i], cmap='gray')

    plt.show()


if __name__ == '__main__':
    filename = input("Please enter filename: ")
    frame_no = int(input("Frame number: "))
    print(filename)
    frames = open_frame(
        filename, ConfigurationStephen, frame_no)

    display_frames(frames)
