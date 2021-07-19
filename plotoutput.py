# Plotting subroutines for inclusion in ipynbs
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.pyplot import figure
import pickle
import numpy as np

alex_magnet_height = lambda x: 35.61 - (float(x.split("_")[-3][1:])/100)
L_magnet = 12.7 * 1e-3 # 12.7mm

config_to_use = {
    # amelia stuff
    '6-jan': (constants.ConfigurationJan67,  lambda x: float(x.split("_")[3].split("/")[0][:-2]) + 1),
    '7-jan': (constants.ConfigurationJan7,  lambda x: float(x.split("_")[3].split("/")[0][:-2]) + 1),
    '9-dec': (constants.ConfigurationDecember9, lambda x: float(x.split("_")[2].split("/")[0][:-2]) + 7.45),
    '19-dec': (constants.ConfigurationDec19, lambda x: float(x.split("-")[2].split("/")[0][:-2]) + 7.45),
    # alexs stuff
    'Dec10-11': (constants.ConfigurationDec10_2020, alex_magnet_height),
    'Jan12-13': (constants.ConfigurationJan12_2021, alex_magnet_height),
    'Jan27-28': (constants.ConfigurationJan27_2021, alex_magnet_height),
    'May2021': (constants.ConfigurationMay2021, alex_magnet_height),
}

def get_config(filename):
    pickle_filename = filename.replace(r"file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/",
                                      r"C:/Users/acor102/Documents/ferrofluids/data/pickled/amelia_data/").replace(".avi", ".p")

    config_id = pickle_filename.split(r"/")[8]
    configuration, mag_lambda = config_to_use[config_id]
    return configuration

def graph_time_series(filenames, summary_data,
                      times=None, graph_function=None,
                      color_function=None, label_function=None,
                      to_pickle_function=None, xlabel="Time from impact (seconds)",
                      title="", ylabel="",
                      set_min_max=False,
                      color_min=170, color_max=300, show_colorbar=False,
                      **kwargs):
    """
    filenames: list of filenames
    summary_data: pandas dataset of the csv file
    times: each one is either a number or a function that takes in the pickled dictionary
           and the files row and returns the start frames. times will be taken from the
           relevant config function multiplied through to this

    """
    colors = []
    if set_min_max:
        for name in filenames:
            row = summary_data[summary_data['filename'] == name].iloc[0]

            if to_pickle_function:
                pickle_fn = to_pickle_function(name)
            else:
                pickle_fn = name.replace(r"file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/",
                                      r"C:/Users/acor102/Documents/ferrofluids/data/pickled/amelia_data/").replace(".avi", ".p")
            p = None
            try:
                p = pickle.load(open(pickle_fn, 'rb'))
            except FileNotFoundError:
                print("ERROR", name)
                continue

            # find filename in csv to pull out weber number and field strength etc
            colors.append(color_function(p, row))

        norm = mpl.colors.Normalize(vmin=min(colors), vmax=max(colors))
        cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.plasma_r)
    else:
        norm = mpl.colors.Normalize(vmin=color_min, vmax=color_max)
        cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.plasma_r)

    # DATA HANDLING
    for name in filenames:
        # convert to the pickle filename

        if to_pickle_function:
            pickle_fn = to_pickle_function(name)
        else:
            pickle_fn = name.replace(r"file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/",
                                  r"C:/Users/acor102/Documents/ferrofluids/data/pickled/amelia_data/").replace(".avi", ".p")
        p = None
        p = pickle.load(open(pickle_fn, 'rb'))

        # find filename in csv to pull out weber number and field strength etc
        row = summary_data[summary_data['filename'] == name].iloc[0]

        color = None
        if color_function:
            color = cmap.to_rgba(color_function(p, row))

        label = None
        if label_function:
            label = label_function(p, row)
        else:
            label = "We {:.0f}".format(row['pre impact weber number'])

        time_series = None
        if graph_function:
            time_series = graph_function(p, row)
        else:
            time_series = p['contact_width'] * 1e3

        pre_impact_frame = p['pre_impact_frame']
        if times is None:
            t = (np.arange(0, len(p['contact_width'])) - pre_impact_frame - 1)/2000 # 2000 fps
        elif False: #times.type is numpy array:
            t = times
        elif  False: #times is a function:
            t = times(p, row)
        if color:
            plt.plot(t, time_series, label=label, color=color)
        else:
            plt.plot(t, time_series, label=label)

    cmap.set_array([])
    plt.gcf().colorbar(cmap) #, ticks=c)


    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.legend()

def graph_phase_plot(summary_data,
                     x_axis_function=lambda p, row: row['vertical field strength'],
                     y_axis_function=lambda p, row: row['pre impact weber number'],
                     color_function=None,
                     set_min_max=False,
                     color_min=0, color_max=20,
                     to_pickle_function=None, xlabel="Field strength",
                     title="", ylabel="Weber number",
                      **kwargs):
    """
    filenames: list of filenames
    summary_data: pandas dataset of the csv file
    times: each one is either a number or a function that takes in the pickled dictionary
           and the files row and returns the start frames. times will be taken from the
           relevant config function multiplied through to this

    """
    colors = []
    if set_min_max:
        for index, row in summary_data.iterrows():
            # convert to the pickle filename
            name = row['filename']

            if to_pickle_function:
                pickle_fn = to_pickle_function(name)
            else:
                pickle_fn = name.replace(r"file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/",
                                      r"C:/Users/acor102/Documents/ferrofluids/data/pickled/amelia_data/").replace(".avi", ".p")
            p = None
            try:
                p = pickle.load(open(pickle_fn, 'rb'))
            except FileNotFoundError:
                print("ERROR", name)
                continue

            # find filename in csv to pull out weber number and field strength etc
            colors.append(color_function(p, row))

        norm = mpl.colors.Normalize(vmin=min(colors), vmax=max(colors))
        cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.plasma_r)
    else:
        norm = mpl.colors.Normalize(vmin=color_min, vmax=color_max)
        cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.plasma_r)

    # DATA HANDLING
    for index, row in summary_data.iterrows():
        # convert to the pickle filename

        name = row['filename']

        if to_pickle_function:
            pickle_fn = to_pickle_function(name)
        else:
            pickle_fn = name.replace(r"file://files.auckland.ac.nz/research/ressci201800021-ferrofluids/Amelia/",
                                  r"C:/Users/acor102/Documents/ferrofluids/data/pickled/amelia_data/").replace(".avi", ".p")
        p = None
        try:
            p = pickle.load(open(pickle_fn, 'rb'))
        except FileNotFoundError:
            print("ERROR", name)
            continue

        # find filename in csv to pull out weber number and field strength etc
        row = summary_data[summary_data['filename'] == name].iloc[0]
        color = cmap.to_rgba(color_function(p, row))

        plt.plot(x_axis_function(p, row), y_axis_function(p, row),  'o', color=color)

    cmap.set_array([])
    plt.gcf().colorbar(cmap) #, ticks=c)


    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
