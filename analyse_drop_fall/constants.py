"""
Constants and configruation values for drop fall analysis

If possible all constants used should be inside a configuration
object
"""
import numpy as np

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

    # threshold level should be set to 128 + calculated threshold level

    BACKGROUND_MATCH_THRESHOLD = 80
    DISPLAY_CONTACT_LINE = True

    FULL_SUMMARY = False

    # For volume estimations require more 'correct' values
    # however for contact line the droplet post impact can get
    # hidden due to background subtraction with a maximally
    # 'correct' threshold level
    # modify this accordingly to get the best volume estimation
    # TODO: Document all of this behaviour
    VOLUME_MAXIMUM_FRAME_NO = 20
    VOLUME_THRESHOLD_LEVEL = 147



class ConfigurationStephen(ConfigurationGeneric):
    # Configurable constants
    THRESHOLD_LEVEL = 55  # thresholding the image to pick up the drop
    CROP_DIMENSIONS = (0, 0, 700, 350)
    # crop the image to these dimensions
    # (ystart, xstart, yend, xend)
    PIXELS_TO_MM = 0.028563817267384453
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)
    # Conversion from pixels to meters
    # based on the slide in use

    SUBTRACT_BACKGROUND = True
    BACKGROUND_SUBTRACT_MODE = "MATCH"

    MAGNETIC_FIELDS = {
        "Sm_10mm": 0.159400,
        "Sm_12.5mm": 0.119894,
        "Sm_16.5mm": 0.079920,
        "Sm_23mm": 0.040531
    }



class ConfigurationDecember9(ConfigurationGeneric):
    THRESHOLD_LEVEL = 220
    VOLUME_THRESHOLD_LEVEL = 147

    SUBTRACT_BACKGROUND = True
    CROP_DIMENSIONS = (200, 350, 670, 850)
    MAXIMUM_FRAME_NO = 500

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


class ConfigurationJan67(ConfigurationGeneric):
    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 215 #15.194869987468792
    VOLUME_THRESHOLD_LEVEL = 189.15433782875047
    VOLUME_MAXIMUM_FRAME_NO = 20

    CROP_DIMENSIONS = (40, 150, 620, 750)

    # CROP_DIMENSIONS = None #(10, 200, 650, 700)
    MAXIMUM_FRAME_NO = 500 # NOTE WAS 100 for a lot of the analysis

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 0.02398766543445327
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    MAGNETIC_FIELDS = {
        # NOTE WELL THAT THIS IS QUITE PROBABLY A BAD APPROXIMATION,
        # also the seperation distance better explains everything in this case
        'touch': 0.21848694544240535,
        'from_top_4.0mm': 0.1741,
        'from_top_7.2mm': 0.12618471664578843,
        'from_top_14.2mm_fixed_focs': 0.0606945397480662,
        'from_top_11.85mm': 0.07438536511997773,
        'from_top_27.9mm': 0.01962988949079673
    }


class ConfigurationJan7(ConfigurationGeneric):
    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 225 #15.194869987468792
    VOLUME_THRESHOLD_LEVEL = 156.42938253753385
    VOLUME_MAXIMUM_FRAME_NO = 20

    CROP_DIMENSIONS = (80, 120, 620, 700)

    # CROP_DIMENSIONS = None #(10, 200, 650, 700)
    MAXIMUM_FRAME_NO = 500 # NOTE WAS 100 for a lot of the analysis

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 0.02398766543445327
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    MAGNETIC_FIELDS = {
        # NOTE WELL THAT THIS IS QUITE PROBABLY A BAD APPROXIMATION,
        # also the seperation distance better explains everything in this case
        'touch': 0.21848694544240535,
        'from_top_4.0mm': 0.1741,
        'from_top_7.2mm': 0.12618471664578843,
        'from_top_14.2mm_fixed_focs': 0.0606945397480662,
        'from_top_11.85mm': 0.07438536511997773,
        'from_top_27.9mm': 0.01962988949079673
    }




class ConfigurationDec19(ConfigurationGeneric):
    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 200#15.194869987468792

    VOLUME_THRESHOLD_LEVEL = 154.67429632098296
    VOLUME_MAXIMUM_FRAME_NO = 20

    CROP_DIMENSIONS = (30, 150, 700, 750)

    MAXIMUM_FRAME_NO = 100

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 0.023729739453340507
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    MAGNETIC_FIELDS = {
        'from_top-6.2mm': 0.1433414746205451,
        'from_top-9.2mm': 0.10021824816900637,
    }


class ConfigurationDec19LightingFix(ConfigurationGeneric):
    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 190 #15.194869987468792
    CROP_DIMENSIONS = (30, 150, 500, 750)

    # CROP_DIMENSIONS = None #(10, 200, 650, 700)
    MAXIMUM_FRAME_NO = 100

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 0.023729739453340507
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    MAGNETIC_FIELDS = {
        'from_top-6.2mm': 0.1433414746205451,
        'from_top-9.2mm': 0.10021824816900637,
    }


class ConfigurationTouch(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True
    THRESHOLD_LEVEL = 240
    CROP_DIMENSIONS = (30, 0, 800, 1023)

    FRAMES_PER_SECOND = 1000

    PIXELS_TO_MM = 0.02398766543445327
    PIXELS_TO_METERS = PIXELS_TO_MM * 10**(-3)

    MINIMUM_DROPLET_AREA = 20

    SUBTRACT_BACKGROUND = True
    MAXIMUM_FRAME_NO = 200

    GET_MAX_CONTACT = False

    MAGNETIC_FIELDS = {
        'touch': 0.21848694544240535,
    }

# Below are Alex's config things
# I'll probably redo them though
class ConfigurationDec10_2020(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True

    ### Need to ask what this is
    THRESHOLD_LEVEL = 190 #15.194869987468792
    VOLUME_THRESHOLD_LEVEL = 189.15433782875047
    VOLUME_MAXIMUM_FRAME_NO = 4000

    CROP_DIMENSIONS = (0, 100, 350, 700)

    MAXIMUM_FRAME_NO = 4000

    GET_MAX_CONTACT = False

    # PIXELS_TO_MM = 1/(24.25)
    PIXELS_TO_MM = (np.sqrt(2) * 4)/136.7

    PIXELS_TO_METERS = PIXELS_TO_MM * 10 ** (-3)

    MAGNETIC_FIELDS = {
        'touch': 0.21848694544240535,
    }



class ConfigurationJan12_2021(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True

    THRESHOLD_LEVEL = 146 #15.194869987468792, was 215
    VOLUME_THRESHOLD_LEVEL = 189.15433782875047
    VOLUME_MAXIMUM_FRAME_NO = 4000

    CROP_DIMENSIONS = (0, 0, 620, 750)

    MAXIMUM_FRAME_NO = 4000

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 4/89.0

    #PIXELS_TO_MM = 1/(22.5)
    PIXELS_TO_METERS = PIXELS_TO_MM * 10 ** (-3)

class ConfigurationJan27_2021(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True

    THRESHOLD_LEVEL = 156 #15.194869987468792 was 215
    VOLUME_THRESHOLD_LEVEL = 189.15433782875047
    VOLUME_MAXIMUM_FRAME_NO = 4000

    CROP_DIMENSIONS = (0, 0, 620, 750)

    MAXIMUM_FRAME_NO = 4000

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 1/(20)
    PIXELS_TO_METERS = PIXELS_TO_MM * 10 ** (-3)

class ConfigurationMay2021(ConfigurationGeneric):

    SUBTRACT_BACKGROUND = True

    THRESHOLD_LEVEL = 165 #15.194869987468792 was 215
    VOLUME_THRESHOLD_LEVEL = 189.15433782875047
    VOLUME_MAXIMUM_FRAME_NO = 4000

    CROP_DIMENSIONS = (0, 0, 620, 750)

    MAXIMUM_FRAME_NO = 4000

    GET_MAX_CONTACT = False

    PIXELS_TO_MM = 4/107.0
    PIXELS_TO_METERS = PIXELS_TO_MM * 10 ** (-3)
