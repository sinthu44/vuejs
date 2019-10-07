""" Socket Server Class. """
import socket
import threading
import time
import ssl
import shutil
from app.backend.tcp_socket.socket_client import SocketClient
from app.manage import _DJANGO_IP, _DJANGO_PORT
from datetime import datetime
import os
import json
import numpy as np
import cv2
import copy
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "0.0.1"


# optional params
_HOST = "0.0.0.0"
_PORT = 8443
_SSL_CERT_FILE = "libs/cert.pem" 
_SSL_KEY_FILE = "libs/key.pem"
_PESON_VECTORIZE_MODEL_KEY = 'person_vectorizer_hn_model' # person_vectorizer_hn_model or person_vectorizer_model

# Define image size param
_WIDTH_PX = 110
_HEIGH_PX = 165

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


def create_socket(host, port, ssl_cert_file=None, ssl_key_file=None):
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
    print('TCP Socket server stated at {}:{}'.format(host, port))

    ssl_sock = ssl_context.wrap_socket(
        sock, server_side=True, do_handshake_on_connect=True)
    ssl_sock.listen(1000)

    return ssl_sock, ssl_context

def save_frame(img_bytes, name_bytes, json_bytes, data_dir, frame_id_api):
    """This function converts body data which received from camera IP, from bytes datatype
    to original datatype

    Args: 
        img_bytes: bytes, bytes of image data which was received from camera IP 
        name_bytes: bytes, bytes of camera name data which was received from camera IP
        json_bytes: bytes, bytes of json data which was received from camera IP
        count: int, number of count value for saving data

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
        if not os.path.isdir(subfol):
            os.mkdir(subfol)
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
    cv2.imwrite(json_data['frame_url'], mRGB)
    # Save bbox images
    ratio = float(_HEIGH_PX)/float(_WIDTH_PX)
    track_id_api = []
    frames_api = {}
    if 'obj_boxes' in json_data.keys():
        for obj_id, obj in enumerate(json_data['obj_boxes']):
            sub_track_id_api = {}
            if obj['recognition']['modelID'] == _PESON_VECTORIZE_MODEL_KEY:
                bbox_coords = obj['detection']['box_geometry_origin']
                bbox_img_np = mRGB[bbox_coords[0]:bbox_coords[2], bbox_coords[1]:bbox_coords[3], :]
                bbox_embeds = obj['recognition']['confidence']
                obj['bbox_url'] = os.path.join(bbox_folder, obj['BoxID']+'.jpg')
                # Resize and padding bbox image
                heigh, width, _ = bbox_img_np.shape
                real_ratio = float(heigh)/float(width)
                if real_ratio < ratio:
                    top = (width * ratio - heigh) / 2
                    bottom = (width * ratio - heigh) - top
                    bbox_img_np= cv2.copyMakeBorder(bbox_img_np, int(top), int(bottom), 0, 0, cv2.BORDER_CONSTANT)
                else:
                    left = (heigh/ratio - width) / 2
                    right = (heigh/ratio - width) - left
                    bbox_img_np= cv2.copyMakeBorder(bbox_img_np, 0, 0, int(left), int(right), cv2.BORDER_CONSTANT)
                # Save bbox image
                cv2.imwrite(obj['bbox_url'], bbox_img_np)
                obj['embedding'] = bbox_embeds
                sub_track_id_api['id'] = obj_id
                sub_track_id_api['label'] = obj['BoxID']
                sub_track_id_api['url'] = obj['bbox_url'].replace(data_dir, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static')
                track_id_api.append(sub_track_id_api)
            else: 
                json_data['obj_boxes'].pop(obj_id)
    frames_api['id'] = frame_id_api
    frames_api['name'] = json_data['timestamp'] + '.'
    frames_api['url'] = json_data['frame_url'].replace(data_dir, 'http://' + _DJANGO_IP + ':' + _DJANGO_PORT + '/static')
    frames_api['trackIDs'] = track_id_api

    # Save json file
    with open(os.path.join(json_folder, json_data['timestamp']+'.json'), 'w') as outfile:
        json.dump(json_data, outfile)

    # draw(mRGB, name)   
    return time_frame, frames_api, name_cam

class SocketServer():
    """ TODO: Update description! """

    version = "1.0.0-rc2"

    def __init__(self, 
                 port=_PORT, 
                 host=_HOST, 
                 ssl_cert_file=_SSL_CERT_FILE, 
                 ssl_key_file=_SSL_KEY_FILE,
                 is_debug=False,
                 is_running=True,
                 is_flushing=True,
                 is_recording=False,
                 verbose=True):
        """ TODO: Add function description! """
        self.ssl_cert_file = ssl_cert_file
        self.ssl_key_file = ssl_key_file
        self.port = port
        self.host = host
        self.verbose = verbose
        self.socket, self.ssl_context = create_socket(self.host, self.port, self.ssl_cert_file, self.ssl_key_file)
        
        # initialize list of connected sockets
        self.queuing_clients = []
        self.recording_clients = [] 
        self.flags = {
            'is_running'  : is_running,
            'is_flushing' : is_flushing,
            'is_recording': is_recording,
            'queuing_client_num': 0,
            'recording_cam_num': 0,
        }

        # initialize threads
        self.record_thread = None

        self.listen() # start the listening thread
        self.flush() # start the flushing thread
        if is_debug:
            self.log()

    def listen(self):
        """ Listen method for the socket server. 

        Args:
            None.

        Returns:
            None.
        """
        def listen_fn(sock, clients, flags):
            """ Function to handle the socket server. 
            
            Args:
                sock
                clients
                ssl_context
                flags

            Returns:
                None.
            """
            while flags['is_running']:
                sub_addr = None
                sub_sock = None
                try:
                    sub_sock, sub_addr = sock.accept()
                except Exception as ex:
                    print('Server has exception when accept new connection: {}'.format(ex))

                if sub_sock is not None:
                    client = SocketClient(socket=sub_sock,
                                          last_active_ts=datetime.now(),
                                          flags={
                                              'is_running': True,
                                              'is_recording': False,
                                              'flush_num': 0,
                                              'recording_start_ts': None,
                                              'recording_time': 0,
                                              'frame_id_api':0,
                                              'data_api': [],
                                              'name_cam': ""
                                          })
                    # client.start() # start the sub thread handling the client 
                    clients.append(client) # save client to the `clients` list

        self.listening_thread = threading.Thread(
            target=listen_fn,
            args=(self.socket, self.queuing_clients, self.flags, )
        )
        self.listening_thread.start()

    def flush(self):
        """ Flush method (receive data but ignore all) of the socket server.

        Args:
            None.

        Returns:
            None.
        """
        def flush_fn(clients, flags, verbose):
            while flags['is_flushing']:
                for client in clients:
                    if verbose:
                        print("Flushing thread handles client {}".format(client.socket))
                    if (client.flags['is_recording'] == False) and (client.flags['is_running'] == True):
                        frame_num = len(client.frames)
                        if frame_num > 0 and client.flags['flush_num'] == 0:
                            client.flags['flush_num'] = frame_num
                time.sleep(2.0) # flush every 5 second 

        self.flushing_thread = threading.Thread(
            target=flush_fn, 
            args=(self.queuing_clients, self.flags, self.verbose, )
        )
        self.flushing_thread.start()

    def clean(self):
        """ Clean disconnected | closed socket's thread.

        Args:
            None.

        Returns:
            None.
        """
        def clean_fn(clients, verbose):
            while True:
                client_num = len(clients)
                for i in range(client_num):
                    client = clients[i]
                    if (client.flags['is_running'] == False):
                        if verbose:
                            print("Join the handle_thread of the cliend {}".format(client))
                        client.close() # close the client handle thread
                        clients.remove(client)

        self.clean_thread = threading.Thread(
            target=clean_fn, 
            args=(self.queuing_clients, self.verbose, )
        )
        self.clean_thread.start()

    def log(self):
        """ Log method to print out the connected clients for the socket server. 
        
        Args:
            None.

        Returns:
            None.
        """
        def log_fn(clients, verbose):
            while True:
                if verbose:
                    print("Socket server log at {}".format(datetime.now()))
                    print("There are {} clients connected.".format(len(clients)))
                client_num = len(clients)
                for client in clients[:client_num]:
                    frames = client.frames
                    if verbose:
                        print("  - Client {}, with {} frames".format(client.socket, len(frames)))
                if verbose:
                    print("******************************")
                time.sleep(5.0)

        self.log_thread = threading.Thread(
            target=log_fn,
            args=(self.queuing_clients, self.verbose, )
        )
        self.log_thread.start()

    def record(self, data_dir='/tmp/debug_videos', record_duration=100):
        """ Record method for saving received data into file database.

        Args:
            None.
        
        Returns:
            None.
        """
        def record_fn(clients, server_flags, data_dir='/tmp/debug_videos', record_duration=10):
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
            while server_flags['is_recording']:
                for client in clients:
                    if client.flags['is_recording']:
                        # print("There are {} frames be saved for the client {}".format(len(client.frames), client))
                        if client.flags['is_running'] == False:
                            client.flags['is_recording'] = False  
                            server_flags['recording_cam_num'] -= 1
                            with open(os.path.join(data_dir, client.flags['name_cam'], client.flags['name_cam'] + '.json'), 'w') as outfile:
                                json.dump({'data':{'frames':client.flags['data_api']}}, outfile) # ?? still issue here!
                            #clients.remove(client) # I wanna move this into the clean thread for handling 
                        elif client.flags['flush_num'] == 0:
                            frames = copy.deepcopy(client.frames)
                            frame_num = len(frames)
                            if frame_num > 0:
                                for frame in frames:
                                    json_bytes, img_bytes, name_bytes = frame
                                    time_frame, frames_api, name_cam = save_frame(img_bytes, name_bytes, json_bytes, data_dir, client.flags['frame_id_api'])
                                    if client.flags['recording_start_ts'] is None:
                                        client.flags['recording_start_ts'] = time_frame
                                    validate_time = time_frame - client.flags['recording_start_ts']
                                    client.flags['name_cam'] = name_cam
                                    client.flags['recording_time'] = validate_time
                                    client.flags['frame_id_api'] += 1
                                    client.flags['data_api'].append(frames_api)
                                    if validate_time > record_duration:
                                        client.flags['is_recording'] = False
                                        server_flags['recording_cam_num'] -= 1
                                        # Save json file
                                        with open(os.path.join(data_dir, name_cam, name_cam + '.json'), 'w') as outfile:
                                            json.dump({'data':{'frames':client.flags['data_api']}}, outfile)
                                        print('break1')
                                        break
                                client.flags['flush_num'] = frame_num # remove saved frames
                if server_flags['recording_cam_num'] == 0: # stop recording
                    server_flags['is_recording'] = False      

        # prepare data_dir
        if os.path.isdir(data_dir):
            shutil.rmtree(data_dir)
        os.mkdir(data_dir)    

        # remove not `is_running` clients
        not_running_clients = [client for client in self.queuing_clients if client.flags['is_running'] == False]
        for client in not_running_clients:
            self.queuing_clients.remove(client)

        # try stop the previous `record_thread`
        if self.record_thread is not None:
            self.record_thread.join()

        client_num = len(self.queuing_clients)
        if (client_num > 0) and (self.flags['is_recording']==False):
            self.data_dir = data_dir
            self.record_duration = record_duration
            self.flags['recording_cam_num'] = client_num
            self.flags['is_recording'] = True
            for client in self.queuing_clients[:client_num]:           
                if client.flags['is_recording'] == False:
                    client.flags['is_recording'] = True
                    client.flags['recording_start_ts'] = None
                    client.flags['recording_time'] = 0
                    client.flags['frame_id_api'] = 0
                    client.flags['data_api'] = []
                    client.flags['name_cam'] = ""
                else:
                    raise ValueError("Client {} is recording stream!".format(client.socket))
            
            self.record_thread = threading.Thread(
                target=record_fn,
                args=(self.queuing_clients, self.flags, self.data_dir, self.record_duration)
            )
            self.record_thread.start() 
        else:
            print("~~~~~ There is no clients for recording! ~~~~~~")
