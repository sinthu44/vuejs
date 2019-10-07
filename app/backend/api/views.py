from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import simplejson as json
from libs.debug_video_server import check_ssl, socket_server, monitor_connections
from libs.socket_server import SocketServer
import threading

@csrf_exempt
def get_cam_list(request):
    if request.method == "GET":
        with open('app/backend/json_data/cam_list.json') as f:
            result = json.load(f)
        return HttpResponse(json.dumps(result))
    else:
        return HttpResponseBadRequest("POST is not allowed!")

def get_image_by_cam():
    pass 

def get_object_tracking():
    pass 

