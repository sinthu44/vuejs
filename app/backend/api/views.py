"""This module creates all APIs for debug video server
"""

import os
import re
import glob
import time
import random
import shutil
import threading
import simplejson as json
from datetime import datetime
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from app.manage import _DJANGO_IP, _DJANGO_PORT
from app.backend.settings import DEBUG
from app.backend.api.utils import *
from app.backend.api.utils import _400_ERROR, _404_ERROR, _500_ERROR
from app.backend.tcp_socket.socket_server import check_ssl, SocketServer
from app.backend.person_reid.person_reid import PersonReIdentifier

# Define datapath, django server IP and Port
_DATA_DIR = '/tmp/debug_videos'

# Define region constant
_CONST_CAM_FOLDER_PREFIX = "cam"

# Define server state enumeration
_SVR_ST_READY_VIEW = 0
_SVR_ST_READY_RECORD = 1
_SVR_ST_RECORDING = 2
_SVR_ST_NOT_READY_RECORD = 3

# Define default time parameters
_DURATION = 0
_RECORDING_TIME = 0
_RECORDING_SIZE_PER_CAM_PER_SEC = 0.02 # (GB)
_MODEL_VERSION = ""

# Check SSL for accept connection to TCP socket server
try:
    check_ssl()
except Exception as ex:
    print(ex)
_SERVER_STATE = _SVR_ST_NOT_READY_RECORD

# TCP Socket Server
server = None

# Create Person ReID engine
person_reider = PersonReIdentifier()

# API Function 
@csrf_exempt 
def start_recording(request):
    """This function listens and process POST request from client to start recording camera IP
    It is used for `Start recording video from stream with duration input API`

    Args:
        request, http request object

    Returns:
        HttpResponse with status 204 if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method=="POST" and len(request.body)>5:
        try:
            global _DURATION
            global _MODEL_VERSION
            global server
            person_reider.__init__()
            data = json.loads(request.body.decode('utf-8'))
            _DURATION = int(data['duration']) 
            _MODEL_VERSION = data['modelVersion']
            server = SocketServer(model_version=_MODEL_VERSION, record_duration=_DURATION)
            server.record()
            return HttpResponse(status=204)
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))
    
@csrf_exempt
def stop_recording(request):
    """This function listens and process POST request from client to stop recording camera IP
    It is used for `Stop recording video from stream API`

    Args:
        request, http request object

    Returns:
        HttpResponse with status 204 if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method == "POST":
        try:
            global server
            if server is not None:
                server.stop(True)
            return HttpResponse(status=204)
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR ), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))

@csrf_exempt
def get_server_state(request):
    """This function listens and process GET request from client check server state and return to client
    It is used for `Check state of server API`

    Args:
        request, http request object

    Returns:
        HttpResponse with data json if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method == "GET":
        try: 
            global server
            global _DURATION
            global _RECORDING_TIME
            if server is None:
                if is_ready_view_video_fn(_DATA_DIR, _MODEL_VERSION) :
                    _SERVER_STATE = _SVR_ST_READY_VIEW 
                    _MAX_DURATION = 3600
                else:
                    _SERVER_STATE = _SVR_ST_READY_RECORD
                    _DURATION = 0 
                    _RECORDING_TIME = 0
                    _MAX_DURATION = 3600
            else:
                server_state = server.get_state() # initializing, recording, preprocessing, finished
                is_hot_stop = server.is_hot_stopped()
                print("Server state: {}".format(server_state), _MODEL_VERSION)
                if server_state == 'initializing':
                    _SERVER_STATE = _SVR_ST_RECORDING
                    _RECORDING_TIME = 0
                    _MAX_DURATION = 3600
                elif server_state == 'recording':
                    _SERVER_STATE = _SVR_ST_RECORDING
                    if not is_hot_stop:
                        _RECORDING_TIME = min(int(100*server.get_recording_time()/_DURATION), 100)
                    _MAX_DURATION = 3600
                elif server_state == 'processing':
                    _SERVER_STATE = _SVR_ST_RECORDING
                    if not is_hot_stop:
                        _RECORDING_TIME = 100
                    _MAX_DURATION = 3600
                elif server_state == 'finished':
                    server = None
                    _SERVER_STATE = _SVR_ST_RECORDING
                    if not is_hot_stop:
                        _RECORDING_TIME = 100
                    _MAX_DURATION = 3600
                else:
                    pass 
            data = {
                "data":{
                    "status": _SERVER_STATE,
                    "duration": _DURATION,
                    "recording_time": _RECORDING_TIME,
                    "max_duration": int(_MAX_DURATION)
                }
            }
            # response
            return HttpResponse(json.dumps(data))
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))


@csrf_exempt
def get_video_frames(request, cam_id):
    """This function listens and processes GET request from client to return the video frames
    for the given cam_id. 

    Args:
        request, http request object
        cam_id (int): ID of the selected camera

    Returns:
        HttpResponse with data json if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method == 'GET':
        try:
            with open(os.path.join(_DATA_DIR, 'cam'+str(cam_id), 'cam'+str(cam_id)+'.json'), 'r') as f:
                json_data = json.load(f)
            json_data['data']['camId'] = cam_id
            json_data['data']['fps'] = 5
            return HttpResponse(json.dumps(json_data))
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR ), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))

@csrf_exempt
def get_cam_list(request):
    """This function listens and process GET request from client check all available cameras list and return to client
    It is used for `List all available cameras API`

    Args:
        request, http request object

    Returns:
        HttpResponse with data json if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method == "GET":
        try:
            all_camera = get_cam_list_fn(_DATA_DIR, _MODEL_VERSION)
            cameras = [{"id":int(re.search(r'\d+', cam).group()),"name":cam} for (i,cam) in enumerate(all_camera)]
            data = {
                "data": cameras
            }
            # JSON serialize response data
            json_data = json.dumps(data)
            # response
            return HttpResponse(json_data)
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR ), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))

@csrf_exempt
def get_reID_objects(request, cam_id, frame_id, track_id):
    """This function listens and processes GET request from client to return the reID objects
    for the given `track_id` at the given `cam_id` and `frame_id`.

    Args:
        request, http request object
        cam_id (str): ID of the selected camera
        frame_id (str): ...
        track_id (str):  ...
        

    Returns:
        HttpResponse with data json if successfully
        HttpResponseBadRequest if not successfully
    """
    if request.method == 'GET':
        try:
            top_num = int(request.GET.get('topNum'))
            cam_list = request.GET.get('reIdCams').split(',')
            all_camera = get_cam_list_fn(_DATA_DIR, _MODEL_VERSION)
            all_camera_id = [re.search(r'\d+', cam).group() for cam in all_camera]
        
            # get the bbox_embedding corresponding to the cam_id, frame_id, track_id
            json_filepath_list = sorted(glob.glob(os.path.join(_DATA_DIR, 'cam'+cam_id, 'json/*.json')))
            if (json_filepath_list==[]) or valid_2_list_fn(cam_list, all_camera_id) or (int(frame_id)+1 > len(json_filepath_list)):
                _404_ERROR["data"]["errors"]["detail"] = "Not found data"
                return HttpResponse(json.dumps(_404_ERROR), status=404)
            else:
                json_filepath = json_filepath_list[int(frame_id)]
                with open(json_filepath, 'r') as f:
                    json_fc = json.load(f)
                if int(track_id) >= len(json_fc['obj_boxes']): 
                    _404_ERROR["data"]["errors"]["detail"] = "Not found track ID {}".format(track_id)
                    return HttpResponse(json.dumps(_404_ERROR), status=404)
                else:
                    obj_box = json_fc['obj_boxes'][int(track_id)] # track_id = obj_index
                    bbox_embedding = obj_box['embedding']

                    # query the bbox_embedding to get the retrieved bboxes
                    if person_reider.kd_tree is None:
                        person_reider.build_kdtree(data_dir=_DATA_DIR)
                    if top_num+1 > len(person_reider.bbox_indices):
                        top_num = len(person_reider.bbox_indices)
                    _retrieved_dists, _retrieved_bboxes, _retrieved_frames, _retrieved_bbox_ids, _retrieved_frames_timestamp = \
                        person_reider.search(bbox_embedding, len(person_reider.bbox_indices))
                    
                    # filter by selected cams given in `cam_list`
                    retrieved_cams = [f.split('/')[-3] for f in _retrieved_frames] # retrieved_frames
                    retrieved_dists = []
                    retrieved_bboxes = []
                    retrieved_frames = []
                    retrieved_bbox_ids = []
                    retrieved_frames_timestamp = []
                    for i, cam in enumerate(retrieved_cams):
                        if cam[3:] in cam_list:
                            retrieved_dists.append(_retrieved_dists[i])
                            retrieved_bboxes.append(_retrieved_bboxes[i])
                            retrieved_frames.append(_retrieved_frames[i])
                            retrieved_bbox_ids.append(_retrieved_bbox_ids[i])
                            retrieved_frames_timestamp.append(_retrieved_frames_timestamp[i])

                    retrieved_dists    = retrieved_dists[:top_num]
                    retrieved_bboxes   = retrieved_bboxes[:top_num]
                    retrieved_frames   = retrieved_frames[:top_num]
                    retrieved_bbox_ids = retrieved_bbox_ids[:top_num]
                    retrieved_frames_timestamp = retrieved_frames_timestamp[:top_num]

                    json_data = {
                        'data': {
                            'objects': []
                        }
                    }
                    for i, (bbox_url, frame_url, timestamp) in enumerate(zip(retrieved_bboxes, retrieved_frames, retrieved_frames_timestamp)):
                        json_data['data']['objects'].append(
                            {
                                'id': i,
                                'url': bbox_url.replace(_DATA_DIR, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static'),
                                'frame_url': frame_url.replace(_DATA_DIR, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static'),
                                'name': 'ID' + track_id + ' - ' + frame_url.split('/')[-3] + ' - ' + timestamp
                            }
                        )
                    return HttpResponse(json.dumps(json_data))
        except Exception as err:
            print('Error: ', err)
            return HttpResponse(json.dumps(_500_ERROR ), status=500)
    else:
        return HttpResponseBadRequest(json.dumps(_400_ERROR))


