"""This scipt is used to test streaming video from local computer client to socket server
"""
import os
import socket, ssl
import pickle
import time
import cv2
import numpy as np
import argparse

# Handle input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--video', '-v', required=True, help='Path to video which will be send to socket server')
parser.add_argument('--save', '-n', default="streamingvideo", help='name of saved video')
parser.add_argument('--ip', '-i', default="0.0.0.0", help='socket server host')
parser.add_argument('--port', '-p', default=443, help='socket server port')

def prepare_data(list_header=[1, 2, 4, 8],str_name="streamingvideo", image_path="test.jpg"):
    """ This function prepares data to send to socket server from fake client (local computer
    instead of camera ID)

    Args:
        list_header(list): list which store header data for validating
        str_name(string): name of image to send to socket server
        image_path(string): path to the image which will be send to socket server

    Returns:
        b_data(bytes): data byte which will be send to socket server
    """
    # name
    b_name = bytes(str_name, 'utf-8')
    b_size_name = (len(b_name)).to_bytes(4, byteorder='big')
    # read image
    with open(image_path, "rb") as image:
        Image = image.read()
        b_image = bytearray(Image)
    b_size_image = (len(b_image)).to_bytes(4, byteorder='big')
    b_data = bytes(list_header) + b_size_image + b_size_name + b_name + b_image
    return b_data

if __name__ == "__main__":
    # Argument
    args = parser.parse_args()
    video_path = args.video
    str_name = args.save
    host = args.ip
    port = int(args.port)
    # connect to socket server
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssl_sock = ssl.wrap_socket(s,
                            ca_certs="libs/cert.pem",
                            cert_reqs=ssl.CERT_REQUIRED,
                            ssl_version=ssl.PROTOCOL_TLSv1)
    ssl_sock.connect((host,port))

    # Gennerate data before converting to byte format
    list_header = [1, 2, 4, 8]
    
    # Send video
    cap = cv2.VideoCapture(video_path)
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    
    # Read until video is completed
    count = 0
    print('Start sending video frames to socket server')
    print('All frames is saved in :',str_name)
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        
            # Display the resulting frame
            # cv2.imshow('Frame',frame)
            cv2.imwrite(str_name+".jpg", frame)
            b_total = prepare_data(str_name=str_name+'-'+str(count),
                                    image_path=str_name+".jpg")
            ssl_sock.send(b_total)
            count+=1
            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        # Break the loop
        else: 
            break
    time.sleep(5)
    print(ssl_sock.recv(4096))
    ssl_sock.close()
    # When everything done, release the video capture object
    cap.release()
    # # Closes all the frames
    # cv2.destroyAllWindows()


