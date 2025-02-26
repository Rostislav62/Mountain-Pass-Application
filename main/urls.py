# /Mountain Pass Application/main/urls.py

from django.urls import path, include  # Импортируем path для маршрутов
from main.views import (SubmitDataUpdateView, SubmitDataListView, UploadImageView, SubmitDataView, SubmitDataDetailView,
                        SubmitDataReplaceView, SubmitDataDeleteView, DeletePerevalPhotoView, PerevalPhotosListView,
                        ModerationListView, DecisionPerevalView, SubmitPerevalForModerationView)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    # Маршрут для загрузки изображений
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),

    path('submitData/', SubmitDataView.as_view(), name='submit-data'),  # POST-запросы

    # Маршрут для получения списка перевалов пользователя по email (GET /submitData/?user__email=<email>)
    path('submitData/list/', SubmitDataListView.as_view(), name='submit-data-list'),

    # Маршрут для редактирования существующего перевала (PATCH /submitData/<id>/)
    path('submitData/<int:pk>/', SubmitDataUpdateView.as_view(), name='submit-data-update'),

    # Маршрут для получения информации о конкретном перевале (GET /submitData/<id>/info/)
    path('submitData/<int:pk>/info/', SubmitDataDetailView.as_view(), name='submit-data-detail'),

    # Полное обновление перевала (PUT)
    path('api/passes/<int:pk>/', SubmitDataReplaceView.as_view(), name='submit-data-replace'),

    # Полное удаление перевала (DELETE)
    path('api/passes/<int:pk>/delete/', SubmitDataDeleteView.as_view(), name='submit-data-delete'),

    # Полное удаление фотографии (DELETE photo)
    path('api/passes/<int:pk>/photos/<int:photo_id>/delete/', DeletePerevalPhotoView.as_view(), name='delete-photo'),

    # Получение id фотографии (DELETE photo)
    path('api/passes/<int:pk>/photos/', PerevalPhotosListView.as_view(), name='pereval-photos-list'),

    # список перевалов со статусом "pending".
    path('moderation/', ModerationListView.as_view(), name='moderation-list'),

    # Решение по перевалу (одобрение / отклонение)
    path('moderation/<int:pk>/decision/', DecisionPerevalView.as_view(), name='decision-pereval'),

    # отправление перевала на модерацию (status = "pending").
    path('api/passes/<int:pk>/submit/', SubmitPerevalForModerationView.as_view(), name='submit-pereval'),

    # Добавляем маршруты, например:
    # router.register(r'perevals', views.PerevalViewSet, basename='pereval')
    path('', include(router.urls)),  # Основные маршруты API
]
