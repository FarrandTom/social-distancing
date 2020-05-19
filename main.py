
from calculations.homography import four_point_transform
from calculations.output import setup_figure, animate
from calculations.calibration import calibrate
from inference.detect import get_raw_detections, sort_detections

import numpy as np
import cv2

from matplotlib.animation import FuncAnimation

import json
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

# ----------------------- SETTINGS -----------------------------

with open('settings.json') as f:
    settings = json.load(f)

VIDEO_INPUT_PATH = settings['VIDEO_INPUT_PATH']
VIDEO_OUTPUT_PATH = settings['VIDEO_OUTPUT_PATH']
CALIBRATION_COORDS_PATH = settings['CALIBRATION_COORDS_PATH']
PHYSICAL_DISTANCE = settings['PHYSICAL_DISTANCE']
REFERENCE_HEIGHT = settings['REFERENCE_HEIGHT']
DPI = settings['DPI']

if settings['LOCAL_RUN'] == "False":
    LOCAL_RUN = False
    VISUAL_INSIGHTS_CREDS_PATH = settings['VISUAL_INSIGHTS_CREDS_PATH']
elif settings['LOCAL_RUN'] == "True":
    LOCAL_RUN = True
    DETECTIONS_FILE = settings['DETECTIONS_FILE']

# Do not expose these as user settings as they are slightly confusing, and really for purely asthetic reasons. 
# The birds eye view of the ellipses does not look correct with a 1:1 scale
# so may need to tweak these
ELLIPSE_WIDTH_SCALE = 3 # Matches the aspect ratio of the plots. 
ELLIPSE_HEIGHT_SCALE = 2

# -------------------------------------------------------------

cap = cv2.VideoCapture(VIDEO_INPUT_PATH)

VIDEO_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
VIDEO_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FPS = int(cap.get(cv2.CAP_PROP_FPS))
TOTAL_FRAMES = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(Back.BLUE + f"Welcome to the Social Distance Calculator!")
print(
    f"------------------------------------------- \n"
    f"Preparing to process {Fore.MAGENTA}{TOTAL_FRAMES}{Style.RESET_ALL} frames of {Fore.MAGENTA}{VIDEO_WIDTH}*{VIDEO_HEIGHT}{Style.RESET_ALL} video. \n"
    f"Grabbing input video from: {Style.BRIGHT}{VIDEO_INPUT_PATH}{Style.RESET_ALL} \n"
    f"Output video will be saved to: {Style.BRIGHT}{VIDEO_OUTPUT_PATH}{Style.RESET_ALL} \n"
    f"-------------------------------------------"
)

if not LOCAL_RUN:
    with open(VISUAL_INSIGHTS_CREDS_PATH) as f:
        info = json.load(f)

    CREDENTIALS = info['credentials']
    MODEL_ID = info['model_id']

    print(f"Local run: {Fore.RED}{LOCAL_RUN}{Style.RESET_ALL}")
    print(f"Using the remote inference endpoint: {Style.BRIGHT}{CREDENTIALS['hostname']}{Style.RESET_ALL} \n"
          f"-------------------------------------------"
    )

    raw_detections = get_raw_detections(local_run=LOCAL_RUN,
                                        video_input_path=VIDEO_INPUT_PATH,
                                        credentials=CREDENTIALS,
                                        model_id=MODEL_ID)
else:
    print(f"Grabbing local detections file from: {Style.BRIGHT}{DETECTIONS_FILE}{Style.RESET_ALL}")
    print(f"Local run: {Fore.GREEN}{LOCAL_RUN}{Style.RESET_ALL} \n"
          f"---------------------"
    )
    raw_detections = get_raw_detections(local_run=LOCAL_RUN,
                                        video_input_path=VIDEO_INPUT_PATH,
                                        detections_file=DETECTIONS_FILE)

sorted_detections = sort_detections(raw_detections, TOTAL_FRAMES)

fig, a0, a1, plt = setup_figure(VIDEO_WIDTH, VIDEO_HEIGHT)

scatter = a0.scatter([], [], color="white")
cap.set(cv2.CAP_PROP_POS_FRAMES, 1.0)
res, image = cap.read()
rgb_image = image[..., ::-1]
im = plt.imshow(rgb_image, animated=True)

calibration_coords = calibrate(image, CALIBRATION_COORDS_PATH)
pts = np.array(calibration_coords, dtype = "float32")

# apply the four point tranform to obtain a "birds eye view" of
# the image. M is our homography matrix. This will be used to transform all other points to the same perspective.
warped, M = four_point_transform(image, pts)

animation = FuncAnimation(fig,
                          animate,
                          frames=np.arange(TOTAL_FRAMES),
                          fargs=[cap,
                                 sorted_detections,
                                 M,
                                 im,
                                 scatter,
                                 a0,
                                 a1,
                                 PHYSICAL_DISTANCE,
                                 REFERENCE_HEIGHT,
                                 ELLIPSE_WIDTH_SCALE,
                                 ELLIPSE_HEIGHT_SCALE],
                           interval=1000 / FPS)

animation.save(VIDEO_OUTPUT_PATH, dpi=DPI)
print("Drawing complete!")

# -------------------------------------------------------------