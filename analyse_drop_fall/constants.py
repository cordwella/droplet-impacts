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

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 1
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)
    # in pixels
    MINIMUM_DROPLET_AREA = 60

    CONTACT_LINE_FIRST_FRAME = 2
    CONTACT_LINE_LAST_FRAME = 10
    FRAMES_PER_SECOND = 2000

    SUBTRACT_BACKGROUND = False
    BACKGROUND_SUBTRACT_MODE = 'SUBTRACT'  # other option is 'MATCH'
    # NOTE In this mode this will affect the overall brightness of the
    # image and as such if this is set the threshold level will have to be
    # set differently

    BACKGROUND_MATCH_THRESHOLD = 80
    DISPLAY_CONTACT_LINE = True

    FULL_SUMMARY = False


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

    SUBTRACT_BACKGROUND = True
    BACKGROUND_SUBTRACT_MODE = "MATCH"


class ConfigurationDecember9(ConfigurationGeneric):
    THRESHOLD_LEVEL = 200
    CROP_DIMENSIONS = None

    SUBTRACT_BACKGROUND = True
    CROP_DIMENSIONS = (30, 350, 670, 850)
    MAXIMUM_FRAME_NO = 100

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 1/39.27
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    TOPDOWN_PIXELS_TO_MM = None

    # folder name, field strength in tesla
    MAGNETIC_FIELDS = {
        "SM_6.5mm_sd": 0.06955612718798337,
        "SM_11.5mm_sd": 0.04144297306689245,
        "SM_20mm_sd": 0.02171298130249175,
        "SM_54.55mm_sd": 0.0034110974759958626
    }


class ConfigurationJan9(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 200
    CROP_DIMENSIONS = None

    SUBTRACT_BACKGROUND = True
    CROP_DIMENSIONS = (30, 170, 650, 700)
    MAXIMUM_FRAME_NO = 100

    GET_MAX_CONTACT = False
