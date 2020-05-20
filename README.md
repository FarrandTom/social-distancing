# Introduction :v:
Yes, this is another social distancing implementation. 

**How is it different?**  
:point_right: Easy to follow end-to-end workflow.  
:point_right: Super simple calibration.  
:point_right: Run locally using a [local detections file](https://github.com/FarrandTom/social-distancing/blob/master/data/labels/oxford_snipped_labels.json), or call an external inference service.  
:point_right: Already integrated into [IBM Visual Insights](https://www.ibm.com/products/ibm-visual-insights) for inference calls, and easy to rip and replace with another inference engine.

It is inspired by the fantastic work done by researchers at IIT-Pavis which you can find [here](https://github.com/IIT-PAVIS/Social-Distancing).

**Example output:**

![](./readme_images/sample.gif)

# Get Up and Running! :running::dash:

1. Clone this repository  
`git clone https://github.com/FarrandTom/social-distancing.git`
2. Install the necessary packages in your virtual environment!  
`conda install --file requirements.txt` or `pip install -r requirements.txt`
3. Run `python main.py` to create an output video in `./data/results/output.mp4` based on a sample snippet of Oxford town centre saved at `./data/videos/oxford_snipped.mp4`

# Usage :bulb:

## Adding New Video :film_strip:


## Configuration :toolbox:
### Settings 

The main configuration file is `settings.json`. This is where the bulk of user driven settings can be tweaked and changed. This repository comes pre-populated with settings which allow you to run the tool out of the box:

```
{
    "VIDEO_INPUT_PATH": "./data/videos/oxford_snipped.mp4",
    "VIDEO_OUTPUT_PATH": "./data/results/output.mp4",
    "CALIBRATION_COORDS_PATH": "./calibration_coords.json",
    "LOCAL_RUN": "True",
    "VISUAL_INSIGHTS_CREDS_PATH": "./placeholder_creds.json",
    "DETECTIONS_FILE": "./data/labels/oxford_snipped_labels.json",
    "PHYSICAL_DISTANCE": 100,
    "REFERENCE_HEIGHT": 22.5,
    "DPI": 300
}
```
The table below contains a description of each of the settings in more detail. 

| Name  | Description | Required? |
| ------------- | ------------- | ------------- |
| VIDEO_INPUT_PATH  | Path to the input video which will be processed.  | :ballot_box_with_check: |
| VIDEO_OUTPUT_PATH  | Path to where the output video will be saved.  | :ballot_box_with_check: |
| CALIBRATION_COORDS_PATH  | Path to the four calibration coordinates for the input video. If there is no existing calibration file then this path represents where the new file will be saved once the user has completed calibration.  | :ballot_box_with_check: |
| LOCAL_RUN  | Boolean flag ("True" or "False") indicating whether to use a local detections file (True), or upload the video file to a 3rd party inference service (False). Out of the box remote inference is supported by IBM Visual Insights. | :ballot_box_with_check: |
| VISUAL_INSIGHTS_CREDS_PATH  | If LOCAL_RUN is False, then this will be a path to a credentials file which supplies authentication to a 3rd party inference service.  | Only if LOCAL_RUN is False |
| DETECTIONS_FILE  | If LOCAL_RUN is True, then this will be a path to a .json file which supplies detected object coordinates and frame numbers. For an example [click here](https://github.com/FarrandTom/social-distancing/blob/master/data/labels/oxford_snipped_labels.json).  | Only if LOCAL_RUN is True|
| PHYSICAL_DISTANCE  | The distance in cm required to maintain social distancing  | :ballot_box_with_check: |
| REFERENCE_HEIGHT  | The estimated real world height of detected objects in cm. In this case we are using head detections, and therefore estimate that the average head height is 22.5 cm. | :ballot_box_with_check: |
| DPI  | The quality of the output video in Dots Per Inch (DPI)   | :ballot_box_with_check: |

### Calibration

### Inference

# References :book:
1. https://github.com/IIT-PAVIS/Social-Distancing
2. https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
3. http://www.robots.ox.ac.uk/ActiveVision/Research/Projects/2009bbenfold_headpose/project.html
4. https://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/

![](./readme_images/social_distancing.jpg)
