import cv2
import numpy as np
import itertools


def evaluate_ellipses(coords, draw_ellipse_requirements, ellipse_boxes, PHYSICAL_DISTANCE, REFERENCE_HEIGHT, M):
    """
    Function that does the heavy lifting of calculating the scaled ellipses based upon the detections. 
    Inspired by: https://github.com/IIT-PAVIS/Social-Distancing/blob/master/social-distancing.py#L468
    
    Args:
        coords (list): List of lists of the bounding box detections picked up in the current video frame.
        draw_ellipse_requirements (list): Stores the values required to trace detected ellipses onto the output frame of the video.
        ellipse_boxes (list): List of bounding box coordinates of the detected ellipses. Used to determine overlapping.
        PHYSICAL_DISTANCE (float): Distance in cm used with the REFERENCE_HEIGHT to estimate the scaling factor of the ellipses.
        REFERENCE_HEIGHT (float): Estimated height of the average bounding box in cm. Used to scale the ellipses. 
        M (np.array): 3*3 homography matrix. Used to transform any given point to bird's-eye view perspective.
    """
    
    for coord in coords:
        left, right, top, bottom = coord

        bb_center = np.array(
            [(left + right) / 2, (top + bottom) / 2], np.int32)

        height_of_bbx = top - bottom
        scaling_factor = PHYSICAL_DISTANCE / REFERENCE_HEIGHT 
        calculated_height = round(scaling_factor * height_of_bbx, 2)

        pts = np.array(
            [[bb_center[0], top], [bb_center[0], bottom]], np.float32)
        pts1 = pts.reshape(-1, 1, 2).astype(np.float32)  # (n, 1, 2)
        dst1 = cv2.perspectiveTransform(pts1, M)
        width = int(dst1[0, 0][1] - dst1[1, 0][1])

        # Bounding box surrounding the ellipses, useful to compute whether there is any overlap between two ellipses
        ellipse_bbx = [bb_center[0]-calculated_height, bb_center[0]+calculated_height, bottom-width, bottom+width]
        ellipse_boxes.append(ellipse_bbx)

        ellipse = [int(bb_center[0]), int(bottom),
                    int(calculated_height), int(width)]

        draw_ellipse_requirements.append(ellipse)


def do_overlap(rect1, rect2):
    """
    Checks whether or not two rectangles overlap.
    Source: https://www.geeksforgeeks.org/find-two-rectangles-overlap/

    Args:
        rect1 (list): 4 corner coordinates of the first rectangle.
        rect2 (list): 4 corner coordinates of the second rectangle.
    
    Returns:
        True (bool): Rectangles do overlap.
        False (bool): Rectangles do not overlap.
    """
      
    if (rect1[0] >= rect2[1] or rect2[0] >= rect1[1]):
        return False
    
    if (rect1[3] <= rect2[2] or rect2[3] <= rect1[2]):
        return False

    return True


def evaluate_overlapping(ellipse_boxes, are_coords_overlapped):
    """
    Populates the are_coords_overlapped with the ellipses which are overlapping one another.
    Likely this simple implementation could be made more efficient with a KDTree/RTree.
    Inspired by: https://github.com/IIT-PAVIS/Social-Distancing/blob/master/social-distancing.py#L425

    Args:
        ellipse_boxes (list): List of detected bounding box coordinates with the current frame.
        are_coords_overlapped (list): List of 1 or 0 at the indexes corresponding to the overlapped ellipse. 
    """
    
    for ind1, ind2 in itertools.combinations(list(range(0, len(ellipse_boxes))), 2):
        
        if do_overlap(ellipse_boxes[ind1], ellipse_boxes[ind2]):
            are_coords_overlapped[ind1] = 1
            are_coords_overlapped[ind2] = 1


def trace(frame, coords, draw_ellipse_requirements, are_coords_overlapped):
    """
    Draw the ellipses and head bounding boxes onto the current frame.
    Colour them according to whether they are overlapping or not.
    Inspired by: https://github.com/IIT-PAVIS/Social-Distancing/blob/87431f1ac44ea28002fba8891226effbb0053400/social-distancing.py#L336

    Args:
        frame (np.array): Current frame of the video.
        coords (list): List of the detection coordinates of the current frame. Used to draw head bounding boxes.
        draw_ellipse_requirements (list): List of lists of the ellipse parameters to be drawn i.e. centre, height, width.
        are_coords_overlapped (list): Flags whether the ellipse should be green or red. 
    """

    colours = [(0, 255, 0), (0, 0, 255)]

    i = 0
    for coord in coords:
        # Trace ellipse
        cv2.ellipse(frame,
                    (int(draw_ellipse_requirements[i][0]), int(
                        draw_ellipse_requirements[i][1])),
                    (int(draw_ellipse_requirements[i][2]), int(
                        draw_ellipse_requirements[i][3])), 0, 0, 360,
                    colours[int(are_coords_overlapped[i])], 2)

        # Draw bounding box around head
        cv2.rectangle(frame,
                    (int(coords[i][0]), int(
                        coords[i][2])),
                    (int(coords[i][1]), int(
                        coords[i][3])),
                    colours[int(are_coords_overlapped[i])], 1)

        i += 1

