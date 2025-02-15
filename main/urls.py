#  /Mountain Pass Application/main/urls.py
from django.urls import path  # Импортируем path для маршрутов
from main.views import SubmitDataUpdateView, SubmitDataListView, UploadImageView, SubmitDataView  # Импортируем нужные представления

urlpatterns = [
    # 📌 Маршрут для загрузки изображений
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),

    path('submitData/', SubmitDataView.as_view(), name='submit-data'),  # POST-запросы

    # 📌 Маршрут для получения списка перевалов пользователя по email (GET /submitData/?user__email=<email>)
    path('submitData/list/', SubmitDataListView.as_view(), name='submit-data-list'),

    # 📌 Маршрут для редактирования существующего перевала (PATCH /submitData/<id>/)
    path('submitData/<int:pk>/', SubmitDataUpdateView.as_view(), name='submit-data-update'),


]
