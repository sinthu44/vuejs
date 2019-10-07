"""
"""
from django.urls import path, include
from .views import get_cam_list, get_image_by_cam, get_object_tracking, start_recording, stop_recording

urlpatterns = [
    path('v1/camid-list', get_cam_list),
    path('v1/images', get_image_by_cam),
    path('v1/objectid', get_object_tracking)
]
