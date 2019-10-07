""" Socket Server Class. """
import socket
import threading
import time
import ssl
import shutil
from socket_client import SocketClient
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

def save_frame(img_bytes, name_bytes, json_bytes, data_dir):
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
    for subfol in [cam_folder, json_folder, frame_folder]:
        if not os.path.isdir(subfol):
            os.mkdir(subfol)
    # if not os.path.exists(os.path.join(data_dir, name_cam)):
    #     os.makedirs(json_folder)
    #     os.makedirs(frame_folder)
    # Parse data
    json_str = json_bytes.decode(encoding='UTF-8', errors='strict')
    imdata = np.frombuffer(img_bytes, dtype='uint8')

    mRGB = cv2.imdecode(imdata, cv2.IMREAD_COLOR)
    json_data = json.loads(json_str)
    # Get time 
    time_frame = json_data['timestamp']
    time_frame = datetime.strptime(time_frame, "%Y.%m.%d.%H:%M:%S.%f")
    time_frame = int(time.mktime(time_frame.timetuple()))
    # Save data
    cv2.imwrite(os.path.join(frame_folder, json_data['timestamp']+'.jpg'), mRGB)
    with open(os.path.join(json_folder, json_data['timestamp']+'.json'), 'w') as outfile:
        json.dump(json_data, outfile)
    # draw(mRGB, name)   
    return time_frame

class SocketServer():
    """ TODO: Update description! """

    def __init__(self, 
                 port=_PORT, 
                 host=_HOST, 
                 ssl_cert_file=_SSL_CERT_FILE, 
                 ssl_key_file=_SSL_KEY_FILE,
                 is_debug=False,
                 is_running=True,
                 is_flushing=True,
                 is_recording=False):
        """ TODO: Add function description! """
        self.ssl_cert_file = ssl_cert_file
        self.ssl_key_file = ssl_key_file
        self.port = port
        self.host = host
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
                                              'recording_start_ts': None
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
        def flush_fn(clients, flags):
            while flags['is_flushing']:
                for client in clients:
                    print("Flushing thread handles client {}".format(client.socket))
                    if client.flags['is_recording'] == False:
                        frame_num = len(client.frames)
                        if frame_num > 0 and client.flags['flush_num'] == 0:
                            client.flags['flush_num'] = frame_num
                time.sleep(2.0) # flush every 5 second 

        self.flushing_thread = threading.Thread(
            target=flush_fn, 
            args=(self.queuing_clients, self.flags, )
        )
        self.flushing_thread.start()

    def log(self):
        """ Log method to print out the connected clients for the socket server. 
        
        Args:
            None.

        Returns:
            None.
        """
        def log_fn(clients):
            while True:
                print("Socket server log at {}".format(datetime.now()))
                print("There are {} clients connected.".format(len(clients)))
                client_num = len(clients)
                for client in clients[:client_num]:
                    frames = client.frames
                    print("  - Client {}, with {} frames".format(client.socket, len(frames)))
                print("******************************")
                time.sleep(5.0)

        self.log_thread = threading.Thread(
            target=log_fn,
            args=(self.queuing_clients, )
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

            Args:
                clients
                data_dir

            Returns:
                None.
            """
            while server_flags['is_recording']:
                for client in clients:
                    if client.flags['is_recording']:
                        # print("There are {} frames be saved for the client {}".format(len(client.frames), client))
                        if client.flags['flush_num'] == 0:
                            frames = copy.deepcopy(client.frames)
                            frame_num = len(frames)
                            if frame_num > 0:
                                for frame in frames:
                                    json_bytes, img_bytes, name_bytes = frame
                                    time_frame = save_frame(img_bytes, name_bytes, json_bytes, data_dir)
                                    if client.flags['recording_start_ts'] is None:
                                        client.flags['recording_start_ts'] = time_frame
                                    elif (time_frame - client.flags['recording_start_ts']) > record_duration:
                                        client.flags['is_recording'] = False
                                        server_flags['recording_cam_num'] -= 1
                                        break
                                client.flags['flush_num'] = frame_num # remove saved frames

                if server_flags['recording_cam_num'] == 0: # stop recording
                    server_flags['is_recording'] = False                            
                    
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
                else:
                    raise ValueError("Client {} is recording stream!".format(client.socket))
            # prepare data_dir
            if os.path.isdir(self.data_dir):
                shutil.rmtree(self.data_dir)
            os.mkdir(self.data_dir)
            self.record_thread = threading.Thread(
                target=record_fn,
                args=(self.queuing_clients, self.flags, self.data_dir, self.record_duration)
            )
            self.record_thread.start()
        else:
            print("~~~~~ There is no clients for recording! ~~~~~~")