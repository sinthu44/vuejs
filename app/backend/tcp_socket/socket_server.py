""" Implement the TCP Socket Server. """
import socket
import threading
import time
import ssl
import shutil
import os
import json
import numpy as np
import cv2
import copy
from datetime import datetime
from app.backend.tcp_socket.socket_client import SocketClient
from app.backend.tcp_socket.frame_recorder import FrameRecorder
from app.backend.tcp_socket.socket_client import vprint as print_with_verbose
from app.manage import _DJANGO_IP, _DJANGO_PORT
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "1.0.0-rc2"

# optional params
_HOST = "0.0.0.0"
_PORT = 8443
_SSL_CERT_FILE = "libs/cert.pem" 
_SSL_KEY_FILE = "libs/key.pem"
# _PESON_VECTORIZE_MODEL_KEY = ['person_vectorizer_hn_model', 'person_vectorizer_model']

# Define image size param
_WIDTH_PX = 110
_HEIGH_PX = 165

_WIDTH_FRAME = 561
_HEIGH_FRAME = 335

def sslwrap(func):
    """This function wraps ssl function to force its socket server which 
    can use TLS v1.2

    Args:
        func: object function, ssl wrap function
    
    Returns: 
        bar: object
    """
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar
ssl.wrap_socket = sslwrap

def check_ssl():
    """This function checks ssl certification to open TCP socket server 
    and accept connection from client

    Args: 
        None

    Returns: 
        None
    """
    from urllib.request import urlopen
    import json
    byte_str = urlopen('https://www.howsmyssl.com/a/check').read()
    data = json.loads(byte_str.decode('utf-8'))
    tls_version = data['tls_version']
    print('>>>Support TSL version {}'.format(tls_version))
    print('>>>SSL library version {}'.format(ssl.OPENSSL_VERSION))
    print('>>>SSL API version {}'.format(ssl._OPENSSL_API_VERSION))

def sslwrap(func):
    """This function wraps ssl function to force its socket server which 
    can use TLS v1.2

    Args:
        func: object function, ssl wrap function
    
    Returns: 
        bar: object
    """
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar
ssl.wrap_socket = sslwrap

def load_json_file(fp):
    with open(fp, 'r') as f:
        return json.load(f)

def create_socket(host, port, ssl_cert_file=None, ssl_key_file=None, verbose=False):
    """ Create a socket object based on the given `host` and `port`.

    Args:
        host (str): the host IP address
        port (int): the port for the socket listens to
        ssl_cert_file
        ssl_key_file

    Returns:
        s (socket.socket): socket object obtained
    """
    assert ssl_cert_file is not None
    assert ssl_key_file is not None

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=ssl_cert_file, keyfile=ssl_key_file)
    ssl_context.check_hostname = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print_with_verbose('TCP Socket server stated at {}:{}'.format(host, port), verbose)

    ssl_sock = ssl_context.wrap_socket(
        sock, server_side=True, do_handshake_on_connect=True)
    ssl_sock.listen(1000)

    return ssl_sock, ssl_context

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

class SocketServer(object):
    """ Class TCP Socket Server. """
    version = "0.0.1"

    def __init__(self, 
                 port=_PORT, 
                 host=_HOST, 
                 ssl_cert_file=_SSL_CERT_FILE, 
                 ssl_key_file=_SSL_KEY_FILE,
                 max_deactive_duration = 20,
                 verbose=True,
                 model_version="v1.0",
                 record_duration=100):
        """ Initialization function of the TcpSocketServer class. 
        
        Args:
            port ():
            host ():
            ssl_cert_file ():
            ssl_key_file ():
            init_duration (init): number of seconds for initializing the tcp socket server
            verbose (bool): whether or not display the status message

        Returns:
            None.

        init --> record --> save --> stop
        """
        # check ssl version 
        
        try:
            check_ssl()
        except Exception as ex:
            print(ex)

        # init class attributes
        self.port = port
        self.host = host
        self.ssl_cert_file = ssl_cert_file
        self.ssl_key_file = ssl_key_file
        self.max_deactive_duration = max_deactive_duration
        self.verbose = verbose
        self.model_version = model_version
        self.record_duration = record_duration
        self.socket, self.ssl_context = create_socket(self.host, self.port, self.ssl_cert_file, self.ssl_key_file, self.verbose)
        self.flags = {
            'is_listening': True,
            'is_recording': True,
            'is_processing': True,
            'is_stopped': False,
            'hot_stop': False,
            'ready_for_recording': False,
            'ready_for_processing': False,
            'start_time': datetime.now(),
            'start_recording_time': None,
            'now_time': None,
            'state': None
        }
        self.queuing_clients = []
        self.frame_recorders = []
        self.all_frames = []

        # start threshes 
        self.listen()
        self.record()
        self.preprocess()

    def listen(self):
        """ Listen method for the socket server. 

        Args:
            None.

        Returns:
            None.
        """
        def listen_fn(sock, clients, flags, max_deactive_duration, verbose):
            """ Function to handle the socket server. 
            
            Args:
                sock (??): server socket for listening
                clients (list): list for storing all connected client
                flags

            Returns:
                None.
            """
            while flags['is_listening']:
                if flags['state'] is None:
                    flags['state'] = 'initializing'
                sub_addr = None
                sub_sock = None
                try:
                    sub_sock, sub_addr = sock.accept() # Risk: may be blocked here!
                except Exception as ex:
                    print('Server has exception when accept new connection: {}'.format(ex))
                # create new socket for connecting client if sub_sock is not None
                if sub_sock is not None: 
                    # __init__(self, socket, flags=None, max_deactive_duration=20, verbose=False):
                    print_with_verbose("Get connection from socket {}".format(sub_sock), verbose=True)
                    client = SocketClient(socket=sub_sock,
                                          flags={
                                              'is_running': True,
                                              'is_stopped': False,
                                              'last_active': datetime.now(),
                                              'ready_for_closing': None,
                                              'saved_frame_num': 0
                                          },
                                          max_deactive_duration=max_deactive_duration,
                                          verbose=verbose
                                          )
                    clients.append(client) # save client to the `clients` list
                    print("Number of clients connected so far: {}".format(len(clients)))
                # check flag is_stopped 
                if flags['is_stopped']:
                    flags['is_listening'] = False
                    
            # stop all clients and its threshes
            print("Stop listening!")
            for client in clients:
                client.close()
            sock.close()
            print("close all socket connections!")
            return  

        self.listening_thread = threading.Thread(
            target=listen_fn,
            args=(self.socket, self.queuing_clients, self.flags, self.max_deactive_duration, self.verbose, )
        )
        self.listening_thread.start()

    def record(self, data_dir='/tmp/debug_videos', init_duration=10):
        """ Record method for saving received data into file database.

        Args:
            None.
        
        Returns:
            None.
        """
        def record_fn(clients, recorders, all_frames, flags, data_dir, init_duration, record_duration, _PESON_VECTORIZE_MODEL_KEY):
            """ Record function for storing data frames in the given `clients` to `data_dir`.
            TODO: 
                @anhtt: clean the code for more readable!

            Args:
                clients
                data_dir

            Returns:
                None.
            """
            # Run recording

            while flags['is_recording']:
                if flags['ready_for_recording']:
                    client_num = len(clients)
                    # parse all client frames to all_frames
                    for client in clients[:client_num]:
                        frames = client.get_frame()
                        if frames is not None:
                            all_frames += frames
                    # save all frames
                    if len(all_frames) > 0:
                        recorder = FrameRecorder(
                            data_dir=data_dir, 
                            frames=copy.deepcopy(all_frames), 
                            _PESON_VECTORIZE_MODEL_KEY= _PESON_VECTORIZE_MODEL_KEY
                        )
                        for _ in range(len(all_frames)): all_frames.pop(0)
                    # check whether to stop recording
                    if (datetime.now() - flags['start_recording_time']).total_seconds() > record_duration:
                        self.stop()
                elif (datetime.now() - flags['start_time']).total_seconds() > init_duration:
                    flags['ready_for_recording'] = True
                    flags['start_recording_time'] = datetime.now()
                    flags['state'] = 'recording'
                else:
                    client_num = len(clients)
                    for client in clients[:client_num]:
                        _ = client.get_frame()
                if flags['is_stopped']:
                    break

            # close the thread
            for recorder in recorders:
                recorder.close()
            flags['is_recording'] = False
            print("Stop recording!")
            return
    
        # prepare data_dir
        self._PESON_VECTORIZE_MODEL_KEY = "person_vectorizer_model" if self.model_version == "v1.0" else "person_vectorizer_hn_model"
        if os.path.isdir(data_dir):
            shutil.rmtree(data_dir)
        os.mkdir(data_dir)    
        self.data_dir = data_dir
        self.init_duration = init_duration
        # self.record_duration = record_duration
        # start recording thread
        self.recording_thread = threading.Thread(
                target=record_fn,
                #ecord_fn(clients, flags, data_dir, init_duration, record_duration)
                args=(self.queuing_clients, self.frame_recorders, self.all_frames, self.flags, self.data_dir, self.init_duration, self.record_duration, self._PESON_VECTORIZE_MODEL_KEY, )
            )
        self.recording_thread.start()

    def preprocess(self):
        """ Preprocess data into one big json file for each cam. """
        def preprocess_fn(flags, data_dir, _PESON_VECTORIZE_MODEL_KEY, processing_fn):
            while flags['is_processing']:
                if flags['is_stopped'] and (flags['is_recording'] == False) and (flags['is_listening'] == False):
                    flags['state'] = 'processing'
                    processing_threads = []
                    for sub_dir in os.listdir(data_dir):
                        processing_thread = threading.Thread(
                            target=processing_fn,
                            args=(data_dir, sub_dir, _PESON_VECTORIZE_MODEL_KEY, )
                        )
                        processing_thread.start()
                        processing_threads.append(processing_thread)
                    # waiting all threshes to join
                    for processing_thread in processing_threads:
                        processing_thread.join()
                    flags['is_processing'] = False
                else:
                    pass
            flags['state'] = 'finished'     
        self._PESON_VECTORIZE_MODEL_KEY = "person_vectorizer_model" if self.model_version == "v1.0" else "person_vectorizer_hn_model"
        self.preprocessing_thread = threading.Thread(
            target=preprocess_fn,
            args=(self.flags, self.data_dir,self._PESON_VECTORIZE_MODEL_KEY, self.process_cam)
        )
        self.preprocessing_thread.start()

    def stop(self, is_hot_stopped=False):
        """ Stop the socket server. """
        self.flags['is_stopped'] = True
        self.flags['hot_stop'] = is_hot_stopped
        if self.flags['is_listening']:
            self.fake_tcp_connection(self.port, self.host)
            self.flags['is_listening'] = False
        
    def get_state(self):
        """ Get the socket server state. """
        if self.flags['state'] == 'finished':
            self.listening_thread.join()
            self.recording_thread.join()
            self.preprocessing_thread.join()
        return self.flags['state']

    def is_hot_stopped(self):
        return self.flags['hot_stop']

    def get_recording_time(self):
        if self.flags['state'] == 'recording':
            return (datetime.now() - self.flags['start_recording_time']).total_seconds()
        else:
            return None

    @staticmethod
    def fake_tcp_connection(port, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

    @staticmethod
    def process_cam(data_dir, sub_dir, _PESON_VECTORIZE_MODEL_KEY):
        json_filenames = [fn for fn in os.listdir(os.path.join(data_dir, sub_dir, 'json')) if fn.endswith('json')]
        json_filepaths = sorted([os.path.join(data_dir, sub_dir, 'json', fn) for fn in json_filenames])
        
        json_content = {
            'data': {
                'frames': []
            }
        }

        count = None
        for frame_id_api, _json_fp in enumerate(json_filepaths):
            json_data = load_json_file(_json_fp)
            track_id_api = []
            if 'obj_boxes' in json_data.keys():
                for obj_id, obj in enumerate(json_data['obj_boxes']):
                    try:
                        if obj['recognition']['modelID'] == _PESON_VECTORIZE_MODEL_KEY:
                            track_id_api.append({
                                'id': obj_id, 
                                'label': obj['BoxID'],
                                'url': obj['bbox_url'].replace(data_dir, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static')
                            })
                            if count is None:
                                json_content['model_version'] = _PESON_VECTORIZE_MODEL_KEY
                                count = 1
                        elif count is None:
                            json_content['model_version'] = obj['recognition']['modelID']
                    except:
                        print("Json fp got error is : {}".format(_json_fp))
                        raise ValueError("Error here!")

            json_content['data']['frames'].append({
                'id': frame_id_api,
                'name': json_data['timestamp'] + '.',
                'url': json_data['frame_url'].replace(data_dir, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static'),
                'trackIDs': track_id_api
            })

        with open(os.path.join(data_dir, sub_dir, sub_dir+'.json'), 'w') as outfile:
            json.dump(json_content, outfile)