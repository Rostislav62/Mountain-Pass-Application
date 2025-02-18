#  /Mountain Pass Application/main/views.py

# from main.models import PerevalGpsTracks, PerevalAdded
# from main.services.google_maps import get_google_map_link
import traceback
import os
from main.db_service import DatabaseService
from main.models import PerevalImages, PerevalAdded
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.generics import ListAPIView  # Импортируем базовый класс для списков
from rest_framework.response import Response  # Импортируем объект Response
from rest_framework import status  # Для указания HTTP-статусов
# from django.shortcuts import get_object_or_404  # Удобный метод для получения объекта или 404
from main.models import PerevalAdded  # Импортируем модель Перевала
from main.serializers import SubmitDataSerializer  # Подключаем сериализатор


class SubmitDataView(APIView):
    """API для приёма и получения данных о перевале"""

    def post(self, request):
        """Обрабатывает POST-запрос с данными перевала"""
        print("📥 Полученные данные:", request.data)   # ✅ Логируем входные данные

        try:
            print("📥 Полученные данные:", request.data)

            serializer = SubmitDataSerializer(data=request.data)

            # Проверяем, что данные валидны
            if serializer.is_valid():
                data = serializer.validated_data
                print("✅ Валидированные данные:", data)  # ✅ Логируем после валидации

                # Сохраняем данные в БД
                pereval = DatabaseService.add_pereval(
                    user_email=data['user']['email'],
                    data=data
                )

                # Возвращаем ID созданного объекта
                return Response({"status": 200, "message": None, "id": pereval.id}, status=status.HTTP_201_CREATED)

            # Если данные невалидны – возвращаем ошибку
            print("❌ Ошибка валидации:", serializer.errors)  # ✅ Логируем ошибки сериализации
            return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Выводим полную трассировку ошибки в консоль
            traceback.print_exc()
            return Response({"status": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Получает список перевалов пользователя по email"""
        email = request.query_params.get("user__email")

        if not email:
            return Response({"message": "Требуется email"}, status=status.HTTP_400_BAD_REQUEST)

        perevals = PerevalAdded.objects.filter(user__email=email)
        serializer = SubmitDataSerializer(perevals, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
        image_record = PerevalImages.objects.create(pereval=pereval, data=file_path)


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
        # track_record = PerevalGpsTracks.objects.create(pereval=pereval, track_path=file_path)
        # return Response({"status": 200, "message": "Файл трека загружен", "track_id": track_record.id}, status=status.HTTP_201_CREATED)

        return Response({"status": 200, "message": "Файл трека загружен"}, status=status.HTTP_201_CREATED)


class SubmitDataUpdateView(APIView):
    """Редактирование данных о перевале, если статус `new`"""

    def patch(self, request, pk, *args, **kwargs):
        print("PATCH-запрос получен")  # Проверяем, вызывается ли метод

        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем статус перевала
        if pereval.status != "new":
            return Response(
                {"state": 0, "message": "Редактирование запрещено: статус перевала не `new`"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Запрещаем редактировать ФИО, email и телефон
        data = request.data.copy()
        if "user" in data:
            for field in ["fam", "name", "otc", "email", "phone"]:
                if field in data["user"]:
                    del data["user"][field]  # Удаляем запрещённые поля

        serializer = SubmitDataSerializer(pereval, data=data, partial=True)  # ВАЖНО: `partial=True`

        if serializer.is_valid():
            print("🔍 Данные перед обновлением:", serializer.validated_data)  # Вывод в консоль для проверки
            serializer.save()
            return Response({"state": 1, "message": "Данные успешно обновлены"}, status=status.HTTP_200_OK)
        else:
            print("❌ Ошибка валидации:", serializer.errors)  # Вывод ошибок в консоль
            return Response({"state": 0, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SubmitDataListView(ListAPIView):
    """Получение списка всех перевалов, отправленных пользователем по email."""

    serializer_class = SubmitDataSerializer  # Используем уже существующий сериализатор
    queryset = PerevalAdded.objects.all()  # Базовый QuerySet (отфильтруем позже)

    def get_queryset(self):
        """
        Получаем `email` из параметров запроса и фильтруем перевалы.
        Если email не передан — возвращаем пустой список.
        """
        email = self.request.query_params.get('user__email')  # Получаем email из URL-параметров

        if not email:  # Если email не передан — возвращаем пустой список
            return PerevalAdded.objects.none()

        return PerevalAdded.objects.filter(user__email=email)  # Фильтруем по email
