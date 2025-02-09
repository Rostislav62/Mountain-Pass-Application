#  /Mountain Pass Application/main/urls.py

from django.urls import path
from main.views import SubmitDataView, UploadImageView, UploadTrackView

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),
    path('uploadTrack/', UploadTrackView.as_view(), name='upload-track'),
]
