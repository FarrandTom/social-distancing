import cv2
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from .ellipses import evaluate_ellipses, evaluate_overlapping, trace

from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)


def setup_figure(VIDEO_WIDTH, VIDEO_HEIGHT):
    """
    Sets up the matplotlib figure which will be animated as the final output of the scripts.
    Also sets up the fonts, and colours for the figure. 
    
    Args:
        VIDEO_WIDTH (int): Width of the input video.
        VIDEO_HEIGHT (int): Height of the input video.

    Returns: 
        fig (matplotlib.figure.Figure): Overall matplotlib Figure object.
        a0 (matplotlib.axes._subplots.AxesSubplot): Subplot which will display the bird's-eye view scatter graph, and surrounding ellipse patches. 
        a1 (matplotlib.axes._subplots.AxesSubplot): Subplot which will display the video output with ellipses drawn on.
        plt (matplotlib.pyplot): Pyplot object. Used to display the imagery. 
    """

    # Set plot font
    plt.rcParams["font.family"] = "arial"

    # Plotting code
    fig, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 3]}, sharey=True, sharex=True)

    plt.xlim(0,VIDEO_WIDTH)
    plt.ylim([VIDEO_HEIGHT,0])
    plt.tight_layout()

    a0.set_title("Bird's-eye view")
    a1.set_title("Camera feed")

    a0.set_aspect(3, adjustable='box')

    a0.tick_params(axis='both',
                    which='both',
                    bottom=False,
                    top=False,
                    right=False,
                    left=False)
    a1.tick_params(axis='both',
                    which='both',
                    bottom=False,
                    top=False,
                    right=False,
                    left=False)

    a0.set_facecolor("#3a2e39")

    return fig, a0, a1, plt


def animate(frame, cap, sorted_detections, M, im, scatter, a0, a1, PHYSICAL_DISTANCE, REFERENCE_HEIGHT, ELLIPSE_WIDTH_SCALE, ELLIPSE_HEIGHT_SCALE):
    """
    Animate function which updates the FuncAnimation class used to generate the output video. Processes the current frame of video and
    returns the updated scatter plot coordinates and ellipse patches (for the bird's-eye perspective) as well as the final drawn frame. 

    Args:
        frame (np.array):
        cap (cv2.VideoCapture):
        sorted_detections (dict): Sorted detections of the input video.
                                  Key: frame number
                                  Value: all detections and associated labels within that frame
        M (np.array): 3*3 homography matrix. Used to transform any given point to bird's-eye view perspective.
        im ():
        scatter ():
        a0 (matplotlib.axes._subplots.AxesSubplot): Subplot which will display the bird's-eye view scatter graph, and surrounding ellipse patches. 
        a1 (matplotlib.axes._subplots.AxesSubplot): Subplot which will display the video output with ellipses drawn on.
        PHYSICAL_DISTANCE (float): Distance in cm used with the REFERENCE_HEIGHT to estimate the scaling factor of the ellipses.
        REFERENCE_HEIGHT (float): Estimated height of the average bounding box in cm. Used to scale the ellipses. 
        ELLIPSE_WIDTH_SCALE (float): 
        ELLIPSE_HEIGHT_SCALE (float):

    Returns:
        scatter (matplotlib.collections.PathCollection): Updated scatter plot coordinates of the detections in the current frame.
        patch_list (list): List of the ellipse patches to be added to the current frame's bird's-eye view.
        im (matplotlib.image.AxesImage): Updated array representing the current frame with the ellipses drawn on top. 
    """

    frame_no = frame + 1

    if frame_no == 2:
        print(
            f"{Style.BRIGHT}Processing frames...{Style.RESET_ALL} \n"
            f"---------------------"
        )
    elif frame_no % 20 == 0:
        percent_complete = (int(frame_no) / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * 100
        print(
            f"Frame: {Style.BRIGHT}{frame_no}{Style.RESET_ALL} \n"
            f"{Fore.GREEN}{percent_complete:.2f}%{Style.RESET_ALL} complete \n"
            f"-------------------"
        )

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no - 1)
    res, image = cap.read()

    detections = sorted_detections[frame_no]
    #          LEFT       RIGHT      TOP        BOTTOM
    coords = [[i['xmax'], i['xmin'], i['ymax'], i['ymin']] for i in detections]

    are_coords_overlapped = np.zeros(np.shape(coords)[0])
    draw_ellipse_requirements = []
    ellipse_boxes = []

    # Evaluate ellipses for each body detected 
    evaluate_ellipses(coords,
                    draw_ellipse_requirements,
                    ellipse_boxes,
                    PHYSICAL_DISTANCE,
                    REFERENCE_HEIGHT,
                    M)

    # Evaluate overlapping
    evaluate_overlapping(ellipse_boxes,
                        are_coords_overlapped)

    # Trace results over output frame
    trace(image,
        coords,
        draw_ellipse_requirements,
        are_coords_overlapped)

    rgb_image = image[..., ::-1]
    im.set_array(rgb_image)

    scatter.set_offsets(np.c_[
        [i[0] for i in draw_ellipse_requirements],
        [i[1] for i in draw_ellipse_requirements]
        ]
    )

    #          green      red
    colours = ["#008148", "#f71735"]
    
    # Clear previous patches. Otherwise it will simply keep plotting over the top of itself.
    del a0.patches[:]
    patch_list = []
    for counter, i in enumerate(draw_ellipse_requirements):
        ellipse = patches.Ellipse((i[0], i[1]), i[2]*ELLIPSE_WIDTH_SCALE, i[3]*ELLIPSE_HEIGHT_SCALE,
                                ec="white", 
                                fc=colours[int(are_coords_overlapped[counter])], 
                                alpha=0.3, animated=True)
        patch_list.append(a0.add_patch(ellipse))

    return scatter, patch_list, im