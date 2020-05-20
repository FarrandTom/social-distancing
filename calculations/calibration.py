import cv2
import numpy as np
from scipy.spatial import distance as dist

import json
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)


def get_mouse_click(event, x, y, flags, param):
    """
    Determines the (x, y) coordinates of the mouse click when a user is calibrating a new video.
    Append them to a list of coordinates used to transform the image to a bird's-eye view perspective.

    Args:
        event (int): Integer representing the current user input. 0 for no input.
        x (int): X-coordinate of the cursor
        y (int): Y-coordinate of the cursor
        flags (int): Additional parameters to listen for. Unused in this example.
        param (list): List of additional user parameters. In this example these are:
                    param[0] is the current image (np.array) being displayed
                    param[1] is the list of coordinates which the user has clicked so far
    """

    frame = param[0]
    coords_list = param[1]

    if event == cv2.EVENT_LBUTTONUP:
        cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
        coords_list.append([x, y])
        print(x, y)


def sort_calibration_coords(pts):
    """
    Ensures that the array of calibration coordinates is in the order that the transformation
    function expects i.e. (top_left, top_right, bottom_right, bottom_left) = pts
    Source: https://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/

    Args:
        pts (np.array): Unsorted list of calibration coordinates

    Returns:
        np.array: Correctly ordered list of calibration coordinates
    """

    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    return np.array([tl, tr, br, bl], dtype="float32")


def calibrate(frame, CALIBRATION_COORDS_PATH):
    """
    Reads and sorts the calibration coordinates from a local .json file.
    If there is no .json file then it opens the first frame of the input video, and prompts the user to 
    select four calibration coordinates. These are then sorted, saved to a new .json file, and returned.

    Args:
        frame (np.array): First frame of the input video. Used if there are no existing calibration coordinates.  
        CALIBRATION_COORDS_PATH (str): Path to the local .json to either load/save the calibration coordinates. 

    Returns:
        calibration_coords (list): Sorted list of the coordinates used to transform the input image to the bird's-eye perspective.
    """
    
    try:
        with open(CALIBRATION_COORDS_PATH) as f:
            calibration_coords = np.array(json.load(f), dtype="float32")
            sorted_calibration_coords = sort_calibration_coords(calibration_coords)
        return sorted_calibration_coords
    except FileNotFoundError:
        print(
            f"{Fore.RED}No existing calibration file found.{Style.RESET_ALL} \n"
            f"You will now be prompted to calibrate the system. \n"
            f"The system expects four points in the shape of a rectangle which it uses as reference coordinates to calculate the bird's-eye perspective. \n"
            f"The rectangle should lie in line with the geometry of the video e.g. if there is a road running through the centre of your video, the rectangle should mirror the road's geometry. \n"
            f"--------------------------------------------------------- \n"
            f"There are two main assumptions to bear in mind with this implementation: \n"
            f"1) The ground is a flat plane. \n"
            f"2) The camera viewpoint is in a fixed position. \n"
            f"--------------------------------------------------------- \n"
            f"The first frame of the input video will now be displayed. \n"
            f"Simply click where you wish the four corners of the calibration rectangle to be- a {Fore.GREEN}green{Style.RESET_ALL} dot will be placed wherever you click. \n"
            f"Your calibration coordinates will be saved at {Style.BRIGHT}{CALIBRATION_COORDS_PATH}{Style.RESET_ALL} \n"
            f"---------------------------------------------------------"
        )

        # If .json file is not found then we populate one ourselves by propmting for user input.
        coords_list = []
        cv2.namedWindow("frame")
        cv2.setMouseCallback("frame", get_mouse_click, param=[frame, coords_list])

        # keep looping until the 'q' key is pressed
        while True:
            cv2.imshow("frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if 'c' is pressed then break from the loop
            if key == ord("c"):
                break

            # Now check that coords_list has 4 entries. 
            # NOTE: Can improve this by sorting it correctly.
            if len(coords_list) == 4:
                calibration_coords = np.array(coords_list, dtype="float32")
                sorted_calibration_coords = sort_calibration_coords(calibration_coords)

                # Save as a .json file.
                with open(CALIBRATION_COORDS_PATH, 'w') as outfile:
                    json.dump(coords_list, outfile)

                return sorted_calibration_coords