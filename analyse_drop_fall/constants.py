"""
Constants and configruation values for drop fall analysis

If possible all constants used should be inside a configuration
object
"""


class ConfigurationGeneric(object):
    DENSITY = 1210       # The density of the ferrofluid (kg/m^3)
    SURFACE_TENSION = 0.026  # The surface tension of the ferrofluid

    # maxiumum number of frames to consider
    MAXIMUM_FRAME_NO = 100

    # in pixels
    MINIMUM_DROPLET_AREA = 60

    CONTACT_LINE_FIRST_FRAME = 2
    CONTACT_LINE_LAST_FRAME = 7

    SUBTRACT_BACKGROUND = True
    BACKGROUND_SUBTRACT_MODE = 'SUBTRACT'  # other option is 'MATCH'


class ConfigurationStephen(ConfigurationGeneric):
    # Configurable constants
    THRESHOLD_LEVEL = 35  # thresholding the image to pick up the drop
    CROP_DIMENSIONS = (0, 0, 665, 350)
    # crop the image to these dimensions
    # (ystart, xstart, yend, xend)
    PIXELS_TO_MM = 0.028563817267384453
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)
    # Conversion from pixels to meters
    # based on the slide in use
    FRAMES_PER_SECOND = 2000

    SUBTRACT_BACKGROUND = False
