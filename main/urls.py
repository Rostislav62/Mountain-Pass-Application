#  /Mountain Pass Application/main/urls.py
# from main.views import UploadTrackView, SubmitDataDetailView

from django.urls import path
from main.views import SubmitDataView, UploadImageView, SubmitDataUpdateView, SubmitDataListView

urlpatterns = [
    # path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),
    # path('submitData/<int:pk>/', SubmitDataDetailView.as_view(), name='submit-data-detail'),
    path('submitData/<int:pk>/', SubmitDataUpdateView.as_view(), name='submit-data-update'),
    # Новый маршрут для получения перевалов по email
    path('submitData/', SubmitDataListView.as_view(), name='submit-data-list'),
    # path('uploadTrack/', UploadTrackView.as_view(), name='upload-track'),
]
