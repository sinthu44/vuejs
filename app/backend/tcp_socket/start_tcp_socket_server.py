""" Implement a simple TCP socket server. """
import os
import ssl
import time
import socket
import logging
import threading
from datetime import datetime
from socket_server import SocketServer
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "0.0.1"


# optional params
_HOST = "127.0.0.1"
_PORT = 12345
#_SSL_CERT_FILE = "/Users/anhttra-mac/workspace/d-soft/debug-video-server/libs/cert.pem" 
#_SSL_KEY_FILE = "/Users/anhttra-mac/workspace/d-soft/debug-video-server/libs/key.pem"
_SSL_CERT_FILE = None
_SSL_KEY_FILE = None

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

if __name__ == "__main__":
    try:
        check_ssl()
    except Exception as ex:
        print(ex)

    server = SocketServer(is_debug=True, is_flushing=True)
    while True:
        if len(server.queuing_clients) > 0:
            print("Start recording ...")
            server.record()
            break
    # # server.start()
    # time.sleep(5.0)
    # server.record()
