""" Class for saving frame using thread. """
import os 
import json
import threading
import numpy as np
import cv2
import copy
from datetime import datetime
import time
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "1.0.0"

# optional params
_HOST = "0.0.0.0"
_PORT = 8443
# _PESON_VECTORIZE_MODEL_KEY = ['person_vectorizer_hn_model', 'person_vectorizer_model']

# Define image size param
_WIDTH_PX = 110
_HEIGH_PX = 165

_WIDTH_FRAME = 561
_HEIGH_FRAME = 335

def load_json_file(fp):
    with open(fp, 'r') as f:
        return json.load(f)

def pad_image_fn(img, ratio):
    """This function pads and resize image

    Args:
        img: numpy array, image 
        ratio: float, ratio to pad image

    Returns:
        img: numpy array, result image after padding
    """
    # Resize and padding bbox image
    heigh, width, _ = img.shape
    real_ratio = float(heigh)/float(width)
    if real_ratio < ratio:
        top = (width * ratio - heigh) / 2
        bottom = (width * ratio - heigh) - top
        img = cv2.copyMakeBorder(img, int(top), int(bottom), 0, 0, cv2.BORDER_CONSTANT)
    else:
        left = (heigh/ratio - width) / 2
        right = (heigh/ratio - width) - left
        img = cv2.copyMakeBorder(img, 0, 0, int(left), int(right), cv2.BORDER_CONSTANT)
    return img

def save_frame(json_bytes, img_bytes, name_bytes, data_dir, _PESON_VECTORIZE_MODEL_KEY):
    """This function converts body data which received from camera IP, from bytes datatype
    to original datatype

    Args: 
        img_bytes: bytes, bytes of image data which was received from camera IP 
        name_bytes: bytes, bytes of camera name data which was received from camera IP
        json_bytes: bytes, bytes of json data which was received from camera IP
        data_dir:

    Returns:
        time_frame: int, time data after converting with second(s) unit
    """
    # print('on_received {} byte of data'.format(len(img_bytes)))
    name = name_bytes.decode(encoding='UTF-8', errors='strict')
    # Create folder
    name_cam = name.split('-')[-1]
    cam_folder = os.path.join(data_dir, name_cam)
    json_folder = os.path.join(cam_folder, 'json')
    frame_folder = os.path.join(cam_folder, 'frames')
    bbox_folder = os.path.join(cam_folder, 'bboxes')
    for subfol in [cam_folder, json_folder, frame_folder, bbox_folder]:
        try:
            os.mkdir(subfol)
        except:
            pass
        # if not os.path.isdir(subfol):
        #     os.mkdir(subfol)

    # Parse data
    json_str = json_bytes.decode(encoding='UTF-8', errors='strict')
    imdata = np.frombuffer(img_bytes, dtype='uint8')
    mRGB = cv2.imdecode(imdata, cv2.IMREAD_COLOR)
    json_data = json.loads(json_str)
    # Get time
    time_frame = json_data['timestamp']
    time_frame = datetime.strptime(time_frame, "%Y.%m.%d.%H:%M:%S.%f")
    time_frame = int(time.mktime(time_frame.timetuple()))
    # Save frame image
    json_data['frame_url'] = os.path.join(frame_folder, json_data['timestamp']+'.jpg')
    new_mRGB = pad_image_fn(mRGB, float(_HEIGH_FRAME)/float(_WIDTH_FRAME))
    new_mRGB = cv2.resize(new_mRGB, (_WIDTH_FRAME, _HEIGH_FRAME)) 
    cv2.imwrite(json_data['frame_url'], new_mRGB)
    # Save bbox images
    ratio = float(_HEIGH_PX)/float(_WIDTH_PX)
    track_id_api = []
    frames_api = {}
    _json_data = copy.deepcopy(json_data) # copy another version of json_data to fix bug cannot get more than 2 bboxes
    if 'obj_boxes' in json_data.keys():
        for obj_id, obj in enumerate(_json_data['obj_boxes']):
            sub_track_id_api = {}
            if obj['recognition']['modelID'] == _PESON_VECTORIZE_MODEL_KEY:
                bbox_coords = obj['detection']['box_geometry_origin']
                bbox_img_np = mRGB[bbox_coords[0]:bbox_coords[2], bbox_coords[1]:bbox_coords[3], :]
                bbox_embeds = obj['recognition']['confidence']
                # obj['bbox_url'] = os.path.join(bbox_folder, obj['BoxID']+'.jpg')
                json_data['obj_boxes'][obj_id]['bbox_url'] = os.path.join(bbox_folder, obj['BoxID']+'.jpg')
                # # Resize and padding bbox image
                bbox_img_np = pad_image_fn(bbox_img_np, ratio)
                # Save bbox image
                cv2.imwrite(os.path.join(bbox_folder, obj['BoxID']+'.jpg'), bbox_img_np)
                # obj['embedding'] = bbox_embeds
                json_data['obj_boxes'][obj_id]['embedding'] = bbox_embeds
            else: 
                # json_data['obj_boxes'].pop(obj_id)
                pass

    # Save json file
    with open(os.path.join(json_folder, json_data['timestamp']+'.json'), 'w') as outfile:
        json.dump(json_data, outfile)
    # draw(mRGB, name)   
    # return time_frame, frames_api, name_cam


class FrameRecorder(object):
    """ FrameRecorder class. """

    version = "0.0.1"

    def __init__(self, data_dir, frames, _PESON_VECTORIZE_MODEL_KEY):
        self.data_dir = data_dir
        self.frames = frames
        self._PESON_VECTORIZE_MODEL_KEY = _PESON_VECTORIZE_MODEL_KEY
        self.save()

    def save(self):
        def save_fn(data_dir, frames, _PESON_VECTORIZE_MODEL_KEY):
            for frame in frames:
                save_frame(frame[0], frame[1], frame[2], data_dir, _PESON_VECTORIZE_MODEL_KEY)

        self.saving_thread = threading.Thread(
            target=save_fn,
            args=(self.data_dir, self.frames, self._PESON_VECTORIZE_MODEL_KEY, )
        )
        self.saving_thread.start()

    def close(self):
        self.saving_thread.join()
