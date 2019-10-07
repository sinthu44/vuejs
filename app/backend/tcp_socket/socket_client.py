""" Socket Client Class. """
import socket
import threading
import time
import ssl
import traceback
import sys
import errno
import copy
from datetime import datetime

__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "0.0.1"


def vprint(message, verbose):
    """ Print the message if verbose is True only. 
    
    Args:
        message
        verbose
    
    Return:
        None.
    """
    if verbose:
        print(message)



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
                        total_header_bytes + name_length + img_length]
        name_bytes = buffer[total_header_bytes:
                            total_header_bytes + name_length - 1]
        
        return json_bytes, img_bytes, name_bytes


class SocketClient(object):
    """ Class of the socket client. """

    version = "1.0.0-rc3" # remove flushing option, add is_stopped + monitor deactive duration condition

    def __init__(self, socket, flags=None, max_deactive_duration=5, verbose=False):
        self.socket = socket
        self.flags = flags
        self.max_deactive_duration = max_deactive_duration
        self.verbose = verbose
        self.frames = []
        self.handle() # start the thread handling the client socket

    def handle(self):
        """ Start the thread handling the client socket. 

        Args:
            None.

        Returns:
            None.
        """
        def handle_socket_client_fn(sock, frames, flags, max_deactive_duration, verbose):
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
                    # check the flag `is_stopped`
                    if flags['is_stopped']:
                        flags['is_running'] = False
                        break
                    data = sock.recv(4*1024)
                    if not data or len(data) == 0:
                        time.sleep(0.1)
                        continue
                    buffer.extend(data)
                    total_header_bytes = 20
                    # processing the received data buffer
                    if require_length == 0: # received header
                        require_length, img_length, name_length, json_length = parse_package_info(
                            data, require_header_bytes, total_header_bytes
                        )
                    elif len(buffer) >= require_length:
                        json_bytes, img_bytes, name_bytes = parse_package_data(
                            buffer, img_length, name_length, json_length, total_header_bytes
                        )
                        frames.append((json_bytes, img_bytes, name_bytes)) # on_received method called later
                        sock.sendall(b'OK') # confirm OK for the socket client 
                        buffer = bytearray(0)
                        require_length = 0
                        flags['last_active'] = datetime.now()
                        # check saved_frame_num for pop data ... 
                        # TODO: @anhtt
                        if flags['saved_frame_num'] > 0:
                            for _ in range(flags['saved_frame_num']): _ = frames.pop(0)
                            flags['saved_frame_num'] = 0
                    elif len(buffer) > 10*1024*1024:
                        buffer = bytearray(0)
                        require_length = 0
                        time.sleep(0.05)
                    # check the last active time condition
                    if (datetime.now() - flags['last_active']).total_seconds() > max_deactive_duration:
                        flags['is_stopped'] = True
                        vprint(
                            '~~~~Monitor marked client {} not running, last active {}'.format(sock, flags['last_active']),
                            verbose=verbose
                        )
                        break
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
                    vprint('socket {} handle error: {}'.format(sock, error), verbose)
                    if error.errno == errno.ECONNRESET:
                        flags['is_running'] = False 
                        break
                except Exception as ex:
                    print('catch exception: {}'.format(ex))
                    traceback.print_exc(file=sys.stdout)
                    time.sleep(2.0)
            # close socket if not `is_running` anymore ~ disconnect socket
            sock.close()
            flags['ready_for_closing'] = True

        self.handle_thread = threading.Thread(
            target=handle_socket_client_fn, 
            args=(self.socket, self.frames, self.flags, self.max_deactive_duration, self.verbose, )
        )
        self.handle_thread.start()
        self.flags['ready_for_closing'] = False

    def close(self):
        """ Close the handling socket and join its thread. """
        while True:
            if self.flags['ready_for_closing']:
                self.handle_thread.join()
                break
            elif self.flags['is_stopped'] == False:
                self.flags['is_stopped'] = True

    def get_frame(self):
        """ Get received frame if possible. """
        if self.flags['saved_frame_num'] == 0:
            frame_num = len(self.frames)
            saved_frames = copy.deepcopy(self.frames[:frame_num]) if frame_num > 0 else None
            self.flags['saved_frame_num'] = frame_num
        else:
            saved_frames = None
        return saved_frames
            
            

    # def is_removable(self):
    #     return flags['ready_for_closing']