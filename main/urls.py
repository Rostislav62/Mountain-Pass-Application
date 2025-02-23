#  /Mountain Pass Application/main/urls.py
from django.urls import path # Импортируем path для маршрутов
from main.views import (SubmitDataUpdateView, SubmitDataListView, UploadImageView, SubmitDataView, SubmitDataDetailView,
                        SubmitDataReplaceView, SubmitDataDeleteView, DeletePerevalPhotoView, PerevalPhotosListView,
                        ModerationListView, ApprovePerevalView, RejectPerevalView, SubmitPerevalForModerationView,
                        ApiSettingsView)  # Импортируем нужные представления

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
    path('api/moderation/', ModerationListView.as_view(), name='moderation-list'),

    # подтверждение перевала (status = "accepted").
    path('api/moderation/<int:pk>/approve/', ApprovePerevalView.as_view(), name='approve-pereval'),

    # отклонение перевала (status = "rejected").
    path('api/moderation/<int:pk>/reject/', RejectPerevalView.as_view(), name='reject-pereval'),

    # отправление перевала на модерацию (status = "pending").
    path('api/passes/<int:pk>/submit/', SubmitPerevalForModerationView.as_view(), name='submit-pereval'),

    # Управление настройками API
    path('api/settings/', ApiSettingsView.as_view(), name='api-settings'),
]