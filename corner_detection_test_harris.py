"""
Test harris corner detection

"""
import numpy as np
import cv2
from matplotlib import pyplot as plt

# open image/video frame

# okay so this should work on the drawn contours, I think maybe I'll save one of
# them from the other code to try to find it

# perform corner detection on both it and the thing

# crop area for corner direction?

# eg I could find the droplet and then attempt corner detection
# upon it

# who knows

# two different methods for detecting corners
# harris method, and me just doing my standard bullshit
# but i need to know which one works better for me

# harris is a better and more general algorithm, but mine knows
# what it's looking for rather than just looking for differences


img = cv2.imread('/home/amelia/Documents/ferrofluids/test2.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,3,3,0.04)
ret, dst = cv2.threshold(dst,0.1*dst.max(),255,0)
dst = np.uint8(dst)
ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
for i in range(1, len(corners)):
    print(corners[i])
img[dst>0.1*dst.max()]=[0,0,255]
plt.imshow(img)
plt.show()
# cv2.destroyAllWindows()
