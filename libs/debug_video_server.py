# /usr/bin/python3
import cv2
import ssl
import socket
import errno
import threading
import time
from datetime import datetime
from functools import wraps
import sys
import numpy as np
import traceback
import json
import argparse 
import os
import subprocess

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--duration_time','-d', required=True, help='Duration time for recording video')

'''
*** for c++ client
sudo apt install libssl-dev openssl
*** for server
pip3 install pyopenssl
pip3 install pyasn1

------------- then running scripts:
sudo su
python3 debug_video_server.py
'''

''' 
please use with right version of client base on below change log:
***************************
CHANGE LOG
* 0.0.x: stable TCP socket
* 0.1.x: support TLS
* 0.2.x: support load json
'''

VERSION = '0.2.0'
SSL_CERT_FILE = 'libs/cert.pem'
SSL_KEY_FILE = 'libs/key.pem'

running = True
clients = {}
client_lock = threading.Lock()
windows_lock = threading.Lock()
last_client_cnt = 0


def draw(mat, name):
    """This function visualizes frame data, which was received from camera IP, as image format
    for user

    Args: 
        mat: numpy array, frame which was received from camera IP
        name: string, name of frame which was received from camera IP

    Returns: 
        None
    """
    windows_lock.acquire(True)
    cv2.imshow(name, mat)
    cv2.waitKey(1)
    windows_lock.release()


def on_received(img_bytes, name_bytes, json_bytes, count):
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
    json_folder = os.path.join('/tmp/debug_video', name_cam, 'json')
    frame_folder = os.path.join('/tmp/debug_video', name_cam, 'frames')
    if not os.path.exists(os.path.join('/tmp/debug_video', name_cam)):
        os.makedirs(json_folder)
        os.makedirs(frame_folder)
    # Parse data
    json_str = json_bytes.decode(encoding='UTF-8', errors='strict')
    imdata = np.frombuffer(img_bytes, dtype='uint8')

    mRGB = cv2.imdecode(imdata, cv2.IMREAD_COLOR)
    json_data = json.loads(json_str)
    # Get time 
    time_frame_ori = json_data['timestamp']
    time_frame_conv = datetime.strptime(time_frame_ori, "%Y.%m.%d.%H:%M:%S.%f")
    time_frame_conv = int(time.mktime(time_frame_conv.timetuple()))
    # Save data
    # cv2.imwrite(os.path.join(frame_folder, str(time_frame)+'_'+str(count)+'.jpg'), mRGB)
    # with open(os.path.join(json_folder, str(time_frame)+'_'+str(count)+'.json'), 'w') as outfile:
    #     json.dump(json_data, outfile)
    cv2.imwrite(os.path.join(frame_folder, time_frame_ori+'.jpg'), mRGB)
    with open(os.path.join(json_folder, time_frame_ori+'.json'), 'w') as outfile:
        json.dump(json_data, outfile)
    # draw(mRGB, name)   
    return time_frame_conv


def log_clients(clients, force=True):
    """This function prints log of all clients which connected to TCP socket server 

    Args:
        clients: dict, which stored all connected clients to TCP socket server 
        force: boolean

    Returns:
        None
    """
    global last_client_cnt
    total_thread = len(clients)
    total_ip = len(set([x[0] for x in clients]))
    client_list = list(set([clients[x]['name']
                            for x in clients if len(clients[x]['name']) != 0]))
    client_list.sort()
    total_client = len(client_list)
    if total_client != last_client_cnt:
        print('~' * 20)
        print('{}'.format('\n'.join(client_list)))
        print('>Thread = {}, AWLBOX = {}, Processor = {}'.format(
            total_thread, total_ip, total_client))
        last_client_cnt = total_client
        if total_client == 0:
            command = "lsof -i :8443 | awk '{print $2}'"
            pids = subprocess.check_output(command, shell=True)
            pids = pids.decode("utf-8")
            pids = pids.split('\n')
            command = 'kill -9 {}'.format(' '.join([str(pid) for pid in pids[1:]]))
            os.system(command)
        

def handle_client(conn, addr):
    """This function handles each client which connected to TCP socket server, receives 
    data from client, process data, converts data, tracks client status 

    Args:
        conn: object, ssl TCP object  
        addr: string, client IP address

    Returns:
        None
    """
    global clients
    global client_lock
    global running
    print('Connected by {}'.format(addr))
    log_clients(clients)

    buffer = bytearray(0)
    require_length = 0
    conn.setblocking(0)
    require_header_bytes = bytearray([1, 2, 4, 8, 1, 2, 4, 8])
    count = 0
    first_time = 0
    while clients[addr]['running'] and running:
        try:
            data = conn.recv(4*1024)
            if not data or len(data) == 0:
                time.sleep(0.1)
                # print('received empty')
                continue
            buffer.extend(data)
            total_header_bytes = 20

            if require_length == 0:
                # received header
                if data[0:8] == require_header_bytes:
                    img_length_bytes = data[8:12]
                    name_length_bytes = data[12:16]
                    json_length_bytes = data[16:20]

                    img_length = int.from_bytes(
                        img_length_bytes, byteorder='big', signed=False)
                    name_length = int.from_bytes(
                        name_length_bytes, byteorder='big', signed=False)
                    json_length = int.from_bytes(
                        json_length_bytes, byteorder='big', signed=False)

                    require_length = img_length + name_length + json_length + total_header_bytes
                    # print('size of img/name/json = {}/{}/{}, total_require={}'.format(
                    #     img_length, name_length, json_length, require_length))
                else:
                    print(
                        'skip packet from due to not header found'.format(addr[0]))
            elif len(buffer) >= require_length:
                json_bytes = buffer[total_header_bytes +
                                    name_length + img_length:]
                img_bytes = buffer[total_header_bytes + name_length:
                                   total_header_bytes + name_length + img_length - 1]
                name_bytes = buffer[total_header_bytes:
                                    total_header_bytes + name_length - 1]
                # print('name_bytes = {}'.format(name_bytes))
                try:
                    time_frame = on_received(img_bytes, name_bytes, json_bytes, count)
                except Exception as ex:
                    print(ex)
                    pass
                conn.sendall(b'OK')
                buffer = bytearray(0)
                require_length = 0
                clients[addr]['last_active'] = datetime.now()
                clients[addr]['name'] = name_bytes.decode('utf-8')
                time.sleep(0.05)
                log_clients(clients, False)
                if count == 0 :
                    first_time = time_frame 
                count += 1 
                processed_time = time_frame - first_time
                if processed_time > int(duration_time):
                    break
                # print('received frame from {} - {}'.format(clients[addr]['name'], addr))
            elif len(buffer) > 10*1024*1024:
                buffer = bytearray(0)
                require_length = 0
                time.sleep(0.05)
        except ssl.SSLWantReadError:
            # print('socket {} error: SSL want read'.format(addr))
            pass
        except ssl.SSLWantWriteError:
            # print('socket {} error: SSL want write'.format(addr))
            pass
        except socket.error as error:
            if error.errno == errno.EAGAIN:
                continue
            if error.errno == errno.EWOULDBLOCK:
                time.sleep(0.05)
                continue
            print('socket {} handle error: {}'.format(addr, error))
            if error.errno == errno.ECONNRESET:
                break
        except Exception as ex:
            print('catch exception: {}'.format(ex))
            traceback.print_exc(file=sys.stdout)

    conn.close()

    client_lock.acquire(True)
    del clients[addr]
    client_lock.release()
    print('Disconnected by {}'.format(addr))
    log_clients(clients)

# wrap ssl function to force it use TLS v1.2


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


def socket_server(host, port):
    """This function creates TCP socket server which listens all client

    Args:
        host: string, host address of TCP socket server
        port: int, port address of TCP socket server 

    Returns: 
        None
    """
    global clients
    global client_lock
    global running

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=SSL_CERT_FILE, keyfile=SSL_KEY_FILE)
    ssl_context.check_hostname = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    print('TCP Socket server stated at {}:{}'.format(host, port))

    ssl_sock = ssl_context.wrap_socket(
        sock, server_side=True, do_handshake_on_connect=True)

    ssl_sock.listen(1000)
    while running:
        addr = None
        connstream = None
        try:
            conn, addr = ssl_sock.accept()
            connstream = conn
        except Exception as ex:
            print('Server has exception when accept new connection: {}'.format(ex))
            connstream = None
 
        if connstream is not None:
            t = threading.Thread(target=handle_client,
                                 args=(connstream, addr, ))
            client_lock.acquire(True)
            clients[addr] = {
                'thread': t,
                'conn': connstream,
                'running': True,
                'last_active': datetime.now(),
                'name': '',
            }
            client_lock.release()
            t.start()
        time.sleep(1)  # can handle maximum 1 connect per second
        print('Socket server still running')

    keys = list(clients.keys())
    for addr in keys:
        try:
            clients[addr]['thread'].join()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
    clients = {}

    ssl_sock.close()


def monitor_connections():
    """This function tracks and prints all connection to TCP socket server

    Args:
        None

    Returns:
        None 
    """
    global running
    print('~~~~TCP Server Monitor started')
    while running:
        now = datetime.now()
        try:
            keys = list(clients.keys())
            for addr in keys:
                try:
                    max_duration = 20
                    duration = now - clients[addr]['last_active']
                    # print('~~~~Monitor: {} active last {}'.format(addr, duration))
                    if (duration).total_seconds() > max_duration:
                        clients[addr]['running'] = False
                        print('~~~~Monitor marked client {} not running, last active {}'.format(
                            addr, duration))
                except Exception as ex:
                    print(ex)
                    traceback.print_exc()
            time.sleep(5)
            # print('~~~~Monitor still running')
        except Exception as ex:
            traceback.print_exc()
            print(ex)


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


if __name__ == '__main__':
    global duration_time
    duration_time = 10
    print('Duration time: ', duration_time)
    print('Debug Video server {} start running'.format(VERSION))

    host = '0.0.0.0'
    port = 8443

    try:
        check_ssl()
    except Exception as ex:
        print(ex)

    try:
        running = True
        server = threading.Thread(target=socket_server, args=(host, port, ))
        monitor = threading.Thread(target=monitor_connections, args=())
        server.start()
        monitor.start()

        while running:
            # still working
            time.sleep(10)

    except KeyboardInterrupt:
        print('KeyboardInterrupt=>will stop soon')
        running = False
        pass
    finally:
        server.join()
        monitor.join()
        print('Debug video server stopped')
