import os
import re
import glob
from datetime import datetime
import simplejson as json
import time 

_DATA_DIR = ""
# Error code
_400_ERROR ={
    "data":  {
        "status" : 400,
        "title" : "Bad Request Error",
        "errors": {
            "title":  "Bad Request Error",
            "detail":  "Bad Request Error"
        }
    }
}

_404_ERROR ={
    "data":  {
        "status" : 404,
        "title" : "Not Found Error",
        "errors": {
            "title":  "Not Found Error",
            "detail":  "Not Found Model"
        }
    }
}

_500_ERROR ={
    "data":  {
        "status" : 500,
        "title" : "Internal Server Error",
        "errors": {
            "title":  "Internal Server Error",
            "detail":  "Internal Server Error"
        }
    }
}	

def get_cam_list_fn(data_path, model_version):
    """This function get all available camera and store in a list object

    Args:
        data_path: string, path to the folder stored debug videos

    Return: 
        cam_list: list, list stored all camera name
    """
    # local variable
    if not os.path.exists(data_path):
        return []
    else: 
        cam_list = []
        if model_version == "v1.0":
            model_key = "person_vectorizer_model"
            not_model_key = "person_vectorizer_hn_model"
        else:
            model_key = "person_vectorizer_hn_model"
            not_model_key = "person_vectorizer_model"

        all_cam = os.listdir(data_path)
        for cam in all_cam:
            with open(os.path.join(data_path, cam, cam + '.json'), 'r') as f:
                json_data = json.load(f)
            if 'model_version' in json_data.keys():
                if json_data['model_version'] == model_key:
                    if bool(re.match(r'cam[0-9]+',cam.lower())):
                        cam_list.append(cam)
                elif json_data['model_version'] != not_model_key:
                    if bool(re.match(r'cam[0-9]+',cam.lower())):
                        cam_list.append(cam)
            else:
                if bool(re.match(r'cam[0-9]+',cam.lower())):
                    cam_list.append(cam)    
        return cam_list

def is_ready_view_video_fn(data_path, model_version):
    """This function check if server is ready for viewing video or not

    Args:
        data_path: string, path to the folder stored debug videos

    Returns: 
        True or False
    """
    all_cam = get_cam_list_fn(data_path, model_version)
    video_num = 0
    for cam in all_cam:
        frames = glob.glob(os.path.join(data_path, cam, 'frames/*.jpg'))
        json = glob.glob(os.path.join(data_path, cam, 'json/*.json'))
        if len(frames) == len(json):
            video_num += 1
    return video_num != 0

def compute_recording_time_fn(data_path):
    """This function compute recording time if server is recording

    Args:
        data_path: string, path to the folder stored debug videos

    Returns:
        recording_time: int, recording time with second unit
    """
    list_record_time = []
    all_camera = get_cam_list_fn(data_path)
    recording_time = 0
    for cam in all_camera:
        image_file = os.listdir(os.path.join(data_path,cam,'frames'))
        json_file = os.listdir(os.path.join(data_path,cam,'json'))
        # Validate min time
        start_time = min(image_file).replace(min(image_file).split('.')[-1],'')
        start_time = datetime.strptime(start_time, "%Y.%m.%d.%H:%M:%S.%f.")
        start_time = int(time.mktime(start_time.timetuple()))
        # Validate max time
        current_time = max(image_file).replace(max(image_file).split('.')[-1],'')
        current_time = datetime.strptime(current_time, "%Y.%m.%d.%H:%M:%S.%f.")
        current_time = int(time.mktime(current_time.timetuple()))
        list_record_time.append(current_time - start_time)
    recording_time = max(list_record_time)
    return recording_time

def convert_time_frame_to_second(time_frame):
    """This function converts time frame to second 

    Args:
        time_frame: time frame data format 

    Returns:
        time(s): int
    """
    time_frame = datetime.strptime(time_frame, "%Y.%m.%d.%H:%M:%S.%f")
    return int(time.mktime(time_frame.timetuple()))

def valid_2_list_fn(son_list, parrent_list):
    """This function check if that son list is in parrent list or not 

    Args:
        son_list: list, son list
        parrent_list: list, parrent list
    
    Returns:
        true or false
    """
    tmp_list = [i for i in son_list if i not in parrent_list]
    return tmp_list != []