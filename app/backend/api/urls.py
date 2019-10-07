"""
"""

from django.urls import path, include, re_path
from .views import start_recording, stop_recording, get_video_frames, get_server_state, get_cam_list, get_reID_objects

urlpatterns = [
    path('cameras/recording/start', start_recording),
    path('cameras/recording/stop', stop_recording),
    path('state', get_server_state),
    path('cameras', get_cam_list),
    path('cameras/<int:cam_id>/frames', get_video_frames),
    # ref: https://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get
    re_path(
        r'^cameras/(?P<cam_id>[0-9]+)/frames/(?P<frame_id>[0-9]+)/trackIds/(?P<track_id>[0-9]+)/objects$', 
        get_reID_objects
    )
]
