# Introduction :v:
Yes, this is another social distancing implementation. 

**How is it different?**  
:point_right: Easy to follow end-to-end workflow.  
:point_right: Super simple calibration.  
:point_right: Run locally using a local detections file, or call an external inference service.  
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

# Usage


# References :book:
1. https://github.com/IIT-PAVIS/Social-Distancing
2. https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
3. http://www.robots.ox.ac.uk/ActiveVision/Research/Projects/2009bbenfold_headpose/project.html
4. https://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/

![](./readme_images/social_distancing.jpg)
