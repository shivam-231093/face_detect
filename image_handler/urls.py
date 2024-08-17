from django.urls import path
from .views import handle_image_upload

urlpatterns = [
    path('upload/', handle_image_upload, name='handle_image_upload'),
]
