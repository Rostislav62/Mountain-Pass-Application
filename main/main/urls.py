#  /Mountain Pass Application/main/urls.py
from django.urls import path, re_path  # Импортируем path для маршрутов
from main.views import SubmitDataUpdateView, SubmitDataListView, UploadImageView, SubmitDataView  # Импортируем нужные представления
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    # 📌 Маршрут для загрузки изображений
    path('uploadImage/', UploadImageView.as_view(), name='upload-image'),

    path('submitData/', SubmitDataView.as_view(), name='submit-data'),  # POST-запросы

    # 📌 Маршрут для получения списка перевалов пользователя по email (GET /submitData/?user__email=<email>)
    path('submitData/list/', SubmitDataListView.as_view(), name='submit-data-list'),

    # 📌 Маршрут для редактирования существующего перевала (PATCH /submitData/<id>/)
    path('submitData/<int:pk>/', SubmitDataUpdateView.as_view(), name='submit-data-update'),


]

schema_view = get_schema_view(
    openapi.Info(
        title="Mountain Pass API",
        default_version="v1",
        description="Документация API для Mountain Pass Application",
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
