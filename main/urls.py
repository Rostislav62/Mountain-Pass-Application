#  /Mountain Pass Application/main/urls.py
# from main.views import UploadTrackView

from django.urls import path
from main.views import SubmitDataView, UploadImageView, SubmitDataDetailView 

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),
    path('submitData/<int:pk>/', SubmitDataDetailView.as_view(), name='submit-data-detail'),
    # path('uploadTrack/', UploadTrackView.as_view(), name='upload-track'),
]
