""" Socket Client Class. """
import socket
import threading
import time
import ssl
import traceback
import sys
from datetime import datetime
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "0.0.1"


# optional params
# ...


def parse_package_info(data, require_header_bytes, total_header_bytes):
        """ Parse the first receive data package to get meta information. 
        
        Args:
            data
            require_header_bytes
            total_header_bytes

        Returns
            ...
        """
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
        else:
            require_length = img_length = name_length = json_length = 0

        return require_length, img_length, name_length, json_length


def parse_package_data(buffer, img_length, name_length, json_length, total_header_bytes):
        """ Parse the data from the received buffer. 

        Args:
            buffer
            img_length
            name_length
            json_length
            total_header_bytes
        
        Returns:
            None.
        """
        json_bytes = buffer[total_header_bytes +
                                            name_length + img_length:]
        img_bytes = buffer[total_header_bytes + name_length:
                        total_header_bytes + name_length + img_length - 1]
        name_bytes = buffer[total_header_bytes:
                            total_header_bytes + name_length - 1]
        
        return json_bytes, img_bytes, name_bytes


class SocketClient(object):
    """ Class of the socket client. """
    def __init__(self, socket, last_active_ts=None, flags=None):
        self.socket = socket
        self.last_active_ts = last_active_ts
        self.flags = flags
        self.frames = []
        self.handle() # start the thread handling the client socket

    def handle(self):
        """ Start the thread handling the client socket. 

        Args:
            None.

        Returns:
            None.
        """
        def handle_socket_client_fn(sock, frames, flags):
            """ Handle the socket client.

            Args:
                sock
                addr

            Returns:
                None.
            """
            buffer = bytearray(0)
            require_length = 0
            sock.setblocking(0)
            require_header_bytes = bytearray([1, 2, 4, 8, 1, 2, 4, 8])
            count = 0
            first_time = 0
            while flags['is_running']:
                try:
                    data = sock.recv(4*1024)
                    if not data or len(data) == 0:
                        time.sleep(0.1)
                        continue
                    buffer.extend(data)
                    total_header_bytes = 20
                    
                    if require_length == 0: # received header
                        require_length, img_length, name_length, json_length = parse_package_info(
                            data, require_header_bytes, total_header_bytes
                        )
                    elif len(buffer) >= require_length:
                        json_bytes, img_bytes, name_bytes = parse_package_data(
                            buffer, img_length, name_length, json_length, total_header_bytes
                        )
                        frames.append((json_bytes, img_bytes, name_bytes)) # on_received method called later
                        sock.sendall(b'OK')
                        buffer = bytearray(0)
                        require_length = 0
                        # flush frames if needed
                        if flags['flush_num'] > 0:
                            print("Before flushing: frames length = {}, flush num = {}".format(len(frames), flags['flush_num']))
                            for _ in range(flags['flush_num']): _ = frames.pop(0)
                            flags['flush_num'] = 0 
                            print("After flushing: frames length = {}, flush num = {}".format(len(frames), flags['flush_num']))
                        # time.sleep(2.0)
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
                    time.sleep(2.0)

            # should implement something if `is_running` False
            # ...

        self.handle_thread = threading.Thread(
            target=handle_socket_client_fn, 
            args=(self.socket, self.frames, self.flags, )
        ) 
        self.handle_thread.start()
