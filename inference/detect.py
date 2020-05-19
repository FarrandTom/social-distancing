import logging
import json

import requests
requests.packages.urllib3.disable_warnings()

from tqdm import tqdm
import time 


def get_vision_token(credentials):
    """
    Generate a Visual Insights access token to authenticate the user to use the API.
    Inspired by: https://github.com/IBM/powerai/tree/master/vision/tools/vapi/cli

    Args:
        credentials (dict): Hostname and authentication of the VI instance to be used.

    Returns:
        token_results (dict): Freshly generated access token results for authentication.
    """
    token_results = None

    headers = {'Content-type': 'application/json'}

    jsonStr = {
               'grant_type':'password',
               'username': f'{credentials["Auth"][0]}',
               'password':f'{credentials["Auth"][1]}',
              }

    url = "https://" + credentials["hostname"] + "/visual-insights/api" + "/tokens"
    
    # rsp = post(url, headers=headers, data=json.dumps(jsonStr))
    rsp = requests.post(url, verify=False, headers=headers, data=json.dumps(jsonStr))

    if rsp.ok:
        token_results = rsp.json()
    else:
        logging.error("Failed to getToken; {}".format(rsp.status_code))

    return token_results 


def perform_inference(access_token, hostname, model_id, filepaths):
    """
    Upload video file to the inference endpoint. This kicks off an asynchronous inference event within Visual Insights. 
    This can be called repeatedly using the get_inference_results endpoint.
    Inpsired by: https://github.com/IBM/powerai/tree/master/vision/tools/vapi/cli

    Args:
        access_token (str): Authentication token for Visual Insights.
        hostname (str): URL of the server instance. 
        model_id (str): UID of the model which will be used for inference. 
        filepaths (str): Path to the video file(s) to be uploaded for inference. 
    
    Returns:
        result (dict): Contains the unique inference ID, and the current status of the inference task.
    """
    result = None

    logging.info("@@@ filepaths={}".format(filepaths))
    headers = {'X-Auth-Token': f'{access_token}'}
    
    files = []
    for filepath in filepaths:
        files.append(('files', open(filepath, 'rb')))

    url = "https://" + hostname + "/visual-insights/api" + "/dlapis/" + model_id

    logging.info("uploadFiles: url={}, files={}\n".format(url, files))
    rsp = requests.post(url, verify=False, headers=headers, files=files)

    if rsp.ok:
        result = rsp.json()
    else:
        print(f"ERR: One or more files failed to upload; {rsp.status_code}")
        print(f"ERR: Fault: {rsp.json()['fault']}")

    return result


def get_inference_results(access_token, hostname, inference_id, include_details='true'):
    """
    Call existing inference job to obtain the status, progress, and detections of the inference workload.

    Args: 
        access_token (str): Authentication token for Visual Insights.
        hostname (str): URL of the server instance. 
        inference_id (str): UID of the inference instance which is working.
        include_details (str): true/false flag of whether or not to include the detections in the response header.

    Returns:
        result (dict): Contains the current status, progress through the video inference, and the detections thus far. 
    """
    result = None
    headers = {'X-Auth-Token': f'{access_token}'}
    payload = {'include-details': include_details}
    
    url = "https://" + hostname + "/visual-insights/api" + "/inferences/" + inference_id

    rsp = requests.get(url, headers=headers, params=payload, verify=False)

    if rsp.ok:
        result = rsp.json()
    else:
        print(f"ERR: Could not retrieve endpoint; {rsp.status_code}")
        print(f"ERR: Fault: {rsp.json()['fault']}")

    return result


def get_raw_detections(local_run, video_input_path, detections_file='', credentials={}, model_id=''):
    """
    Get the raw detections of the input video. If being used in local mode this function simply reads
    a .json file containing the detections for the input video. 
    Otherwise, this calls out to the Visual Insights end point.  

    Args: 
        local_run (bool): Determines whether to read a local .json file, or call out to a remote VI instance. 
        video_input_path (str): Path to the input video.
        detections_file (str): Path to the local detections .json file.
        credentials (dict): Hostname and authentication of the VI instance to be used.
        model_id (str): UID of the model which will be used for inference. 

    Returns:
        raw_detections (dict): Bounding box detections and associated labels for each frame in the input video.
    """
    if local_run:
        # NOTE: Using the ground truth detections for now.
        with open(detections_file) as f:
            raw_detections = json.load(f)
        return raw_detections
    else:
        token_results = get_vision_token(credentials)
        access_token = token_results['token']
        print("Visual Insights access token: " + access_token)
        print("Uploading video file...")

        hostname = credentials['hostname']
        upload_results = perform_inference(access_token, hostname, model_id, [video_input_path])
        inference_id = upload_results['_id']
        print("Inference ID: " + inference_id)

        result = get_inference_results(access_token, hostname, inference_id, include_details='false')
        status = result['status']
        with tqdm(total=100, desc='Inference status') as pbar:
            while (status == 'starting') or (status == 'working'):
                time.sleep(2)
                result = get_inference_results(access_token, hostname, inference_id, include_details='false')
                status = result['status']
                pbar.update(float(result['percent_complete']) - pbar.n)

        print(f"------------------")
        raw_detections = result['classified']
        return raw_detections


def sort_detections(raw_detections, total_frames):
    """
    Sorts the raw detections to dictionary where the key is the frame, and the value is a list
    of all of the detections within that frame.

    Args:
        raw_detections (dict): Unordered detections from the input video.
        total_frames (int): Total number of frames in the input video.

    Returns:
        sorted_detections (dict): Sorted detections of the input video.
                                  Key: frame number
                                  Value: all detections and associated labels within that frame
    """

    sorted_detections = {}

    # Create skeleton of final object. This allows us to simply append new dictionaries to it.
    for i in range(total_frames):
        frame_no = i + 1
        sorted_detections[int(frame_no)] = []

    # Populate the skeleton object
    for raw_detection in raw_detections:
        frame_number = int(raw_detection["frame_number"])
        sorted_detections[frame_number].append(raw_detection)

    return sorted_detections
