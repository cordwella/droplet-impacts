
# create a basic phase plot and do analysis on that
# maybe this would be better later as a jupyter notebook, but may as well
# create the graphs here and then move there?
# I dont currently have jupyter setup locally and I don't feel like moving

# open csv with all data using pandas
import pandas as pd
import matplotlib.pyplot as plt


def create_phase_plot(data, first='magnetic field',
                      second_axis="vol pre impact weber number", divisor=None,
                      multi=None, remove_uncertain=False):

    for name, group in data.groupby('classification'):
        if remove_uncertain and name[-1] == 'u':
            continue
        x = group[first]
        y = group[second_axis]

        if divisor:
            y = y/group[divisor]
        if multi:
            y = y * group[multi]
        plt.scatter(y, x, label=name)

    if multi:
        second_axis = second_axis + " * " + multi

    if divisor:
        second_axis = second_axis + "/ " + divisor

    
    plt.ylim(plt.ylim()[::-1])    
    # plt.ylim(plt.ylim()[::-1])
    plt.xlabel(second_axis)
    plt.ylabel(first)
    plt.legend()
    plt.show()
    # setup axis
    # x axis is

data = pd.read_csv("file:///C:/Users/acor102/Documents/ferrofluids data/output-10feb.csv")
#create_phase_plot(data, second_axis="Pre impact weber number",
#                    first="Maximum Spread Height")
create_phase_plot(data) #, "Magnetic field", "Maximum Spread Contact Width",
                  #"Pre impact diameter",
                  # remove_uncertain=True) # ,
                  #"Pre impact diameter")

#                   divisor="Pre impact length")
