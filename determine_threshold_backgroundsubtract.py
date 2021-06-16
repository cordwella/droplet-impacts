"""
Code to determine the optimal thresholding value for
a set of droplet images.

Inputs: File of droplet video, frame number to analyse

It is advisable to run this a few times for differently numbered frames and
to take the average of that. This process can vary wildly depending on lots
of things.

"""
import time

import numpy as np
import matplotlib.pyplot as plt

import cv2


def find_gsv_along_line(image, points, step_size=0.5):
    if points[0, 0] > points[1, 0]:
        points = points[::-1]
    m, c = np.polyfit(points[:, 0], points[:, 1], 1)
    x = np.arange(int(points[0, 0]), int(points[1, 0]) + 1, 0.5)
    y = (m * x + c).astype(int)
    x = x.astype(int)

    gsv = image[y, x]
    return x, gsv


def tellme(s):
    plt.title(s, fontsize=16)
    plt.draw()


def determine_threshold(frame, low_value=0):
    # display frame
    # ask for input points to define line

    plt.clf()
    plt.setp(plt.gca())

    tellme("Place points at the ends of the lines to plot the gsv")
    plt.imshow(frame, cmap='gray')
    # plt.waitforbuttonpress()

    while True:
        pts = []
        while len(pts) < 2:
            pts = np.asarray(plt.ginput(2, timeout=-1))
            if len(pts) < 2:
                time.sleep(1)  # Wait a second

        ph = plt.plot(pts[:, 0], pts[:, 1])

        tellme('Happy? Key click for yes, mouse click for no')

        if plt.waitforbuttonpress():
            break

        # Get rid of fill
        for p in ph:
            p.remove()

    x_values, gsv = find_gsv_along_line(frame, pts)

    # clear the plot
    plt.close()

    plt.title("Gray scale value as a function of x")
    plt.plot(x_values, gsv)

    tellme("Select bottom level")
    while True:
        pts = []
        while len(pts) < 1:
            pts = np.asarray(plt.ginput(1, timeout=-1))
            if len(pts) < 1:
                time.sleep(1)  # Wait a second

        # only care about the y values to draw the line in
        bottom_gsv = pts[0, 1]

        line = plt.axhline(y=bottom_gsv, color='r', linestyle='-')

        tellme('Happy? Key click for yes, mouse click for no')

        if plt.waitforbuttonpress():
            break

        line.remove()

    tellme("Select top level")
    while True:
        pts = []
        while len(pts) < 1:
            pts = np.asarray(plt.ginput(1, timeout=-1))
            if len(pts) < 1:
                time.sleep(1)  # Wait a second

        # only care about the y values to draw the line in
        top_gsv = pts[0, 1]

        line = plt.axhline(y=top_gsv, color='g', linestyle='-')

        tellme('Happy? Key click for yes, mouse click for no')

        if plt.waitforbuttonpress():
            break

        line.remove()

    print("Background Gray Scale Value: ", top_gsv)
    print("Droplet Gray Scale Value: ", bottom_gsv)
    # on the left of the gsv find the two intersection points

    # finding intersections
    # this is currently a fairly cheap way of doing it but who really cares?
    # this is better than nothing and the best way to do it would be to
    # find the next closest point above the line and find the connecting
    # line and then the point there to do it (like what I'm going to do)
    # for finding the exact value rather than the current integer values

    diff = gsv - top_gsv

    # find the region where diff negative
    neg_diff_top = np.asarray(diff < 0).nonzero()[0]
    # find intersection
    # interp only works when values are increasing
    # as I only want the 0 intercept multiplying by negative 1
    # incases where it is decreasing works well
    left_top_intersection = np.interp(
        0, -1 * diff[:neg_diff_top[3]], x_values[:neg_diff_top[3]])
    right_top_intersection = np.interp(
        0, diff[neg_diff_top[-3]:], x_values[neg_diff_top[-3]:])

    diff = bottom_gsv - gsv
    neg_diff_bottom = np.asarray(diff >= 0).nonzero()[0]
    left_bottom_intersection = np.interp(
        0, diff[:neg_diff_bottom[3]], x_values[:neg_diff_bottom[3]])
    right_bottom_intersection = np.interp(
        0, -1 * diff[neg_diff_bottom[-3]:neg_diff_bottom[-3] + 5],
        x_values[neg_diff_bottom[-3]:neg_diff_bottom[-3] + 5])

    left_halfway_point = (left_top_intersection + left_bottom_intersection)/2
    right_halfway_point = (
        right_top_intersection + right_bottom_intersection)/2

    # draw these vertical lines on the graph

    # using numpy interpolation function to find these spots
    left_threshold = np.interp(left_halfway_point, x_values, gsv)
    right_threshold = np.interp(right_halfway_point, x_values, gsv)

    tellme("Thresholding")

    optimal_threshold = (left_threshold + right_threshold)/2
    print("Left threshold", left_threshold)
    print("Right threshold", right_threshold)
    print("Optimal Threshold", optimal_threshold)

    plt.scatter(left_halfway_point, left_threshold, marker='x')
    plt.scatter(right_halfway_point, right_threshold, marker='x')
    plt.show()

    return optimal_threshold


def open_frame(filename, frame_number):
    vidcap = cv2.VideoCapture(filename)

    count = 0
    
    # use first frame to perform background subtraction
    background_image = None    
    success, image = vidcap.read()
    while True:
        # write files to frames
        success, image = vidcap.read()
        if not success:
            raise Exception("Frame not found")
            
    
        if background_image is None:
            background_image = image

        # transform image to only get the first color value
        if count == frame_number:
            image = 255 - abs(image/2 - background_image/2)

            return image[:, :, 0]  # black and white single channel image

        count += 1


if __name__ == '__main__':
    filename = input("Input filename:")
    frame_number = int(input("Frame Number:"))
    frame = open_frame(filename, frame_number)
    threshold = determine_threshold(frame)
