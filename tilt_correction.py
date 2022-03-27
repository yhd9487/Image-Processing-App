import numpy as np
import cv2
import os


# from https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/


def correct_tilt(gui, filepath):
    """This function corrects skewed images - the image may need additional 90° rotation later"""
    image = cv2.imread(filepath)

    # convert the image to grayscale and flip the foreground and background
    # to ensure foreground is now "white" and the background is "black"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    # threshold the image, setting all foreground pixels to 255 and all background pixels to 0
    # binarize the image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # grab the (x, y) coordinates of all pixel values that are greater than zero
    # then use these coordinates to compute a rotated bounding box that contains all coordinates
    # finds all (x, y)-coordinates in the thresh image that are part of the foreground
    coordinates = np.column_stack(np.where(thresh > 0))

    # computes the minimum rotated rectangle that contains the entire text region
    # returns angle values in the range [-90, 0]
    angle = cv2.minAreaRect(coordinates)[-1]
    print("Angle:", angle)

    # as the rectangle rotates clockwise the returned angle trends to 0 --
    # in this special case we need to add 90 degrees to the angle
    # if the angle is less than -45 degrees, then we need to add 90 degrees to the angle and take the inverse

    if angle < -45:
        angle = -(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    #image = rotate_image(image, angle)  # added this function

    # rotate the image to fix tilt
    # determine the center (x, y)-coordinate of the image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # pass the center coordinates and rotation angle into the cv2.getRotationMatrix2D

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # does the rotation
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                             borderValue=(255, 255, 255))

    # read_file = cv2.imread(rotated)
    # save image
    old_file = filepath
    os.remove(filepath)
    cv2.imwrite(old_file, rotated)
    gui.close_image()
    gui.upload_image(filepath)
    return rotated


