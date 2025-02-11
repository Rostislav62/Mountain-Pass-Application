#  /Mountain Pass Application/main/views.py

import traceback
import os
from main.serializers import SubmitDataSerializer
from main.db_service import DatabaseService
from main.models import PerevalImages, PerevalAdded
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from main.models import PerevalGpsTracks, PerevalAdded
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from main.services.google_maps import get_google_map_link


class SubmitDataView(APIView):
    """API для приёма данных о перевале"""

    def post(self, request):
        """Обрабатывает POST-запрос с данными перевала"""
        try:
            serializer = SubmitDataSerializer(data=request.data)

            # Проверяем, что данные валидны
            if serializer.is_valid():
                data = serializer.validated_data

                # Сохраняем данные в БД
                pereval = DatabaseService.add_pereval(
                    user_email=data['user']['email'],
                    data=data
                )

                # Возвращаем ID созданного объекта
                return Response({"status": 200, "message": None, "id": pereval.id}, status=status.HTTP_201_CREATED)

            # Если данные невалидны – возвращаем ошибку
            return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Выводим полную трассировку ошибки в консоль
            traceback.print_exc()
            return Response({"status": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadImageView(APIView):
    """API для загрузки изображений перевалов"""

    def post(self, request):
        """Принимает изображение, сохраняет его и записывает в БД"""

        # Проверяем, есть ли файл в запросе
        if 'image' not in request.FILES:
            return Response({"status": 400, "message": "Файл изображения обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        pereval_id = request.data.get('pereval_id')

        # Проверяем, существует ли перевал
        try:
            pereval = PerevalAdded.objects.get(id=pereval_id)
        except PerevalAdded.DoesNotExist:
            return Response({"status": 400, "message": "Перевал не найден"}, status=status.HTTP_400_BAD_REQUEST)

        # Определяем путь для сохранения файла
        upload_dir = os.path.join(settings.MEDIA_ROOT, "pereval_images")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Сохраняем файл в `MEDIA_ROOT/pereval_images/`
        file_path = os.path.join("pereval_images", image.name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        default_storage.save(full_path, ContentFile(image.read()))

        # Сохраняем путь в БД
        image_record = PerevalImages.objects.create(pereval=pereval, image_path=file_path)

        return Response({"status": 200, "message": "Файл загружен", "image_id": image_record.id}, status=status.HTTP_201_CREATED)


class UploadTrackView(APIView):
    """API для загрузки GPS-треков"""

    def post(self, request):
        """Принимает GPS-трек (GPX/KML), сохраняет его и записывает в БД"""

        # Проверяем, есть ли файл в запросе
        if 'track' not in request.FILES:
            return Response({"status": 400, "message": "Файл трека обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        track = request.FILES['track']
        pereval_id = request.data.get('pereval_id')

        # Проверяем, существует ли перевал
        try:
            pereval = PerevalAdded.objects.get(id=pereval_id)
        except PerevalAdded.DoesNotExist:
            return Response({"status": 400, "message": "Перевал не найден"}, status=status.HTTP_400_BAD_REQUEST)

        # Определяем путь для сохранения файла
        upload_dir = os.path.join(settings.MEDIA_ROOT, "pereval_tracks")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Сохраняем файл в `MEDIA_ROOT/pereval_tracks/`
        file_path = os.path.join("pereval_tracks", track.name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        default_storage.save(full_path, ContentFile(track.read()))

        # Сохраняем путь в БД
        track_record = PerevalGpsTracks.objects.create(pereval=pereval, track_path=file_path)

        return Response({"status": 200, "message": "Файл трека загружен", "track_id": track_record.id}, status=status.HTTP_201_CREATED)





