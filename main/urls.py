# /Mountain Pass Application/main/urls.py

from django.urls import path, include  # Импортируем path для маршрутов
from main.views import (SubmitDataListView, UploadImageView, SubmitDataView, SubmitDataDetailView,
                        SubmitDataDeleteView, DeletePerevalPhotoView, PerevalPhotosListView,
                        ModerationListView, DecisionPerevalView, SubmitPerevalForModerationView, SubmitDataUpdateView,
                        SeasonListView, DifficultyLevelListView, UpdateImageView,
                        )
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    # Маршрут для загрузки изображений
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),

    # Получение списка изображений перевала
    path('uploadImage/photos/<int:pk>/', PerevalPhotosListView.as_view(), name='upload-image-list'),

    # Удаление фотографии
    path('uploadImage/delete/<int:photo_id>/', DeletePerevalPhotoView.as_view(), name='delete-upload-image'),

    # Изменение изображений
    path('uploadImage/<int:image_id>/', UpdateImageView.as_view(), name='update_image'),

    # Запись нового перевала
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),  # POST-запросы

    # Маршрут для получения списка перевалов пользователя по email (GET /submitData/?user__email=<email>)
    path('submitData/list/', SubmitDataListView.as_view(), name='submit-data-list'),

    # Маршрут для получения информации о конкретном перевале (GET /submitData/<id>/info/)
    path('submitData/<int:pk>/info/', SubmitDataDetailView.as_view(), name='submit-data-detail'),

    # Полное удаление перевала (DELETE) перенесено в submitData/
    path('submitData/<int:pk>/delete/', SubmitDataDeleteView.as_view(), name='submit-data-delete'),

    # Добавляем маршрут обновления перевала
    path('submitData/<int:pk>/update/', SubmitDataUpdateView.as_view(), name='submit-data-update'),

    # список перевалов со статусом "pending".
    path('moderation/', ModerationListView.as_view(), name='moderation-list'),

    # Решение по перевалу (одобрение / отклонение)
    path('moderation/<int:pk>/decision/', DecisionPerevalView.as_view(), name='decision-pereval'),

    # отправление перевала на модерацию (status = "pending").
    path('passes/<int:pk>/submit/', SubmitPerevalForModerationView.as_view(), name='submit-pereval'),

    # маршруты для сезонов и сложностей
    path('seasons/', SeasonListView.as_view(), name='season-list'),
    path('difficulty-levels/', DifficultyLevelListView.as_view(), name='difficulty-level-list'),

    # Добавляем маршруты, например:
    path('', include(router.urls)),  # Основные маршруты API
]
