#  /Mountain Pass Application/main/urls.py

from django.urls import path
from main.views import SubmitDataView

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
]
