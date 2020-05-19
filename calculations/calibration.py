import cv2
import numpy as np
import json

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


def sort_calibration_coords(calibration_coords):
    """
    Ensures that the list of calibration coordinates is in the order that the transformation
    function expects i.e. (top_left, top_right, bottom_right, bottom_left) = pts

    Args:
        raw_calibration_coords (list): Unsorted list of calibration coordinates

    Returns:
        sorted_calibration_coords (list): Correctly ordered list of calibration coordinates
    """

    print("You need to write the sort_calibration_coords function Tom!")
    # Order should be top left, top right, bottom right, bottom left
    return calibration_coords


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

            # NOTE: NEED TO ADD SORTING FUNCTION
            sorted_calibration_coords = sort_calibration_coords(calibration_coords)
        return calibration_coords
    except FileNotFoundError:
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

                # NOTE: NEED TO ADD SORTING FUNCTION
                sorted_calibration_coords = sort_calibration_coords(calibration_coords)

                # Save as a .json file.
                with open(CALIBRATION_COORDS_PATH, 'w') as outfile:
                    json.dump(coords_list, outfile)

                return calibration_coords