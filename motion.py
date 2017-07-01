from picamera import PiCamera, Color
from time import sleep
from scipy import ndimage
#from scikit.image.measure import compare_ssim as ssim
import numpy as np
import matplotlib.pyplot as plt
from shutil import copy2
import os
from os.path import basename
import datetime

WORKING_FOLDER = "./working"
DETECTED_FOLDER = "./detected"
MOTION_THRESHOLD = 250

def show_image(image):
    plt.imshow(image)
    plt.show()

#blurs an image
def blur_image(image):
    #print("blur_image")
    blurred =ndimage.gaussian_filter(image, sigma=(8), order=0)
    #print("blur_image exit")
    return blurred

# Calculates the mean square differce between to same sized images.
def mean_squared_diff(image1, image2):
    #print("mean_squared_diff")
    if image1.shape != image2.shape:
        raise ValueError("Images must be of the same size")
    err = np.sum((image1.astype("float") -
                  image2.astype("float")) ** 2)
    err /= float(image1.shape[0]) * float(image1.shape[1])
    #print("mean_squared_diff exit");
    return err

# Loads an image, optionally converting to greyscale, optionally blurring.
def load_image(filename, convert_to_gs = True, blur = False):
    #print("load_image")
    image = ndimage.imread(filename, flatten = convert_to_gs)
    if blur:
        image = blur_image(image)
    #print("load_image exit")
    return image

# This function is called when motion is detected
def motion_detected(file1, file2):
    print("Motion Detected at ", datetime.datetime.now(), file1, file2)
    copy2(file1, DETECTED_FOLDER)
    copy2(file2, DETECTED_FOLDER)
    video = DETECTED_FOLDER + "/" + os.path.basename(file2) + ".h264"
    camera.start_recording(video) # play with omxplayer
    sleep(5)
    camera.stop_recording()

camera = PiCamera()
camera.rotation = 180
camera.resolution = (1280, 960)

#camera.start_preview() # alpha=0..255

# The main detection loop.
i = 0 
while True:
    file = WORKING_FOLDER + "/capture%s.jpg" % i
    camera.capture(file)
    if i >=1: 
        # do the comparison
        previous_file = WORKING_FOLDER + "/capture%s.jpg" % (i - 1)
        if i > 5: # Correct would be >=1 but the first few captures are always a bit dubious.
            image1 = load_image(previous_file)
            image2 = load_image(file)
            diff = mean_squared_diff(image1, image2)
            #diff2 = ssim(image1, image2)
            print (diff)
            if diff > MOTION_THRESHOLD:
                motion_detected(previous_file, file)
        # Tidy up.
        os.remove(previous_file)    
    #sleep(0.5)
    i += 1;

#camera.stop_preview()
