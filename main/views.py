#  /Mountain Pass Application/main/views.py

# from main.models import PerevalGpsTracks, PerevalAdded
# from main.services.google_maps import get_google_map_link
# from django.shortcuts import get_object_or_404  # Удобный метод для получения объекта или 404
# from rest_framework.response import Response  # Импортируем объект Response
# from django.contrib.auth.decorators import login_required  # Проверяем администратора
import traceback
import os
import logging
from main.db_service import DatabaseService
from main.models import PerevalImages
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.generics import ListAPIView  # Импортируем базовый класс для списков
from rest_framework import status  # Для указания HTTP-статусов
from main.models import PerevalAdded  # Импортируем модель Перевала
from main.serializers import SubmitDataSerializer  # Подключаем сериализатор
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema  # 📌 Импортируем Swagger-декоратор Swagger-документация
from drf_yasg import openapi  # 📌 Импортируем для описания параметров
from rest_framework.parsers import MultiPartParser, FormParser  # 📌 Добавляем поддержку загрузки файлов
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from main.serializers import PerevalImagesSerializer  # Подключаем сериализатор
from main.models import ApiSettings  # Импортируем модель
from rest_framework.permissions import IsAdminUser  # Только админы могут изменять настройку
from rest_framework.generics import RetrieveUpdateAPIView  # Используем API для получения/изменения
from main.serializers import ApiSettingsSerializer
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response
from main.models import ModeratorGroup, User
from main.permissions import IsSuperAdmin
from main.serializers import PerevalUserSerializer
from main.permissions import IsModerator


class SubmitDataView(APIView):
    """API для приёма и получения данных о перевале"""

    @swagger_auto_schema(
        request_body=SubmitDataSerializer,  # 📌 Позволяет вводить JSON в Swagger
        manual_parameters=[],  # 📌 Убирает ненужные параметры в UI
        responses={201: openapi.Response("Created", SubmitDataSerializer)},  # 📌 Описывает успешный ответ
    )
    def post(self, request):
        """📌 POST: Создаёт новый перевал"""
        print("📥 Полученные данные:", request.data)  # ✅ Логируем входные данные

        try:
            serializer = SubmitDataSerializer(data=request.data)

            # Проверяем, что данные валидны
            if serializer.is_valid():
                data = serializer.validated_data
                print("✅ Валидированные данные:", data)  # ✅ Логируем после валидации

                # Сохраняем данные в БД
                if not data.get("connect", False):
                    return Response(
                        {"status": 400, "message": "Нет связи. Перевал нельзя отправить."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                pereval = DatabaseService.add_pereval(user_email=data['user']['email'], data=data)

                # Возвращаем ID созданного объекта
                return Response({"status": 200, "message": None, "id": pereval.id}, status=status.HTTP_201_CREATED)

            # Если данные невалидны – возвращаем ошибку
            print("❌ Ошибка валидации:", serializer.errors)  # ✅ Логируем ошибки сериализации
            return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()  # Выводим полную трассировку ошибки в консоль
            return Response({"status": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user__email",
                openapi.IN_QUERY,
                description="📌 Email пользователя для фильтрации перевалов",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: SubmitDataSerializer(many=True)},  # 📌 Описывает успешный ответ
    )
    def get(self, request):
        """📌 GET: Получает список перевалов пользователя по email"""
        email = request.query_params.get("user__email")

        if not email:
            return Response({"message": "Требуется email"}, status=status.HTTP_400_BAD_REQUEST)

        perevals = PerevalAdded.objects.filter(user__email=email)
        serializer = SubmitDataSerializer(perevals, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)  # 🔹 Логирование событий


class UploadImageView(APIView):
    """📌 API для загрузки изображений перевалов"""

    parser_classes = (MultiPartParser, FormParser)  # 🔹 Поддержка загрузки файлов через multipart/form-data

    @swagger_auto_schema(
        operation_description="📌 Загрузка изображения для перевала",
        manual_parameters=[
            openapi.Parameter(
                'pereval_id',
                openapi.IN_FORM,
                description="📌 ID перевала, к которому прикрепляется изображение",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="📌 Файл изображения",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="📌 Название изображения (опционально)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={201: openapi.Response("Файл загружен")}
    )
    def post(self, request):
        """📌 Принимает изображение, сохраняет его и записывает в БД"""

        logger.info("📥 Получен запрос на загрузку изображения.")
        logger.info(f"🔹 Данные запроса: {request.data}")

        # 🔹 Проверяем, переданы ли все нужные данные
        if 'image' not in request.FILES:
            logger.error("❌ Ошибка: Файл изображения не передан.")
            return Response(
                {"status": 400, "message": "Файл изображения обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']  # 🔹 Получаем загружаемый файл
        pereval_id = request.data.get('pereval_id')  # 🔹 Получаем ID перевала
        title = request.data.get('title', image.name)  # 🔹 Если title не передан, используем имя файла

        # 🔹 Проверяем, существует ли перевал с таким ID
        try:
            pereval = PerevalAdded.objects.get(id=pereval_id)
            logger.info(f"✅ Найден перевал ID: {pereval_id}")
        except PerevalAdded.DoesNotExist:
            logger.error(f"❌ Ошибка: Перевал ID {pereval_id} не найден.")
            return Response(
                {"status": 400, "message": "Перевал не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Определяем путь для сохранения файла (создаём папку `pereval_images`, если её нет)
        upload_dir = os.path.join(settings.MEDIA_ROOT, "pereval_images")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            logger.info(f"📂 Создана папка для изображений: {upload_dir}")

        # 🔹 Генерируем уникальное имя файла
        base_name, ext = os.path.splitext(image.name)  # 🔹 Разделяем имя файла и расширение
        counter = 1
        file_name = f"{base_name}{ext}"  # 🔹 Начинаем с оригинального имени
        relative_path = os.path.join("pereval_images", file_name)  # 🔹 Используем ОТНОСИТЕЛЬНЫЙ путь (исправление!)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)  # 🔹 Абсолютный путь для проверки существования

        # 🔹 Если файл с таким именем уже есть, добавляем `_1`, `_2` и т. д.
        while os.path.exists(full_path):
            file_name = f"{base_name}_{counter}{ext}"
            relative_path = os.path.join("pereval_images", file_name)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            counter += 1

        # 🔹 Сохраняем файл
        try:
            default_storage.save(relative_path, ContentFile(image.read()))  # 🔹 Сохраняем ОТНОСИТЕЛЬНЫЙ путь
            logger.info(f"✅ Файл сохранён: {relative_path}")
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении файла: {str(e)}")
            return Response(
                {"status": 500, "message": f"Ошибка при сохранении файла: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 🔹 Записываем в БД путь к файлу и название
        try:
            image_record = PerevalImages.objects.create(
                pereval=pereval,
                data=relative_path,  # 🔹 Сохраняем ОТНОСИТЕЛЬНЫЙ путь в БД
                title=title
            )
            logger.info(f"✅ Изображение записано в БД с ID: {image_record.id}")
        except Exception as e:
            logger.error(f"❌ Ошибка при записи в БД: {str(e)}")
            return Response(
                {"status": 500, "message": f"Ошибка при записи в БД: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"status": 201, "message": "Файл загружен", "image_id": image_record.id},
            status=status.HTTP_201_CREATED
        )


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


class SubmitDataUpdateView(UpdateAPIView):
    """Редактирование данных о перевале, если статус new"""

    queryset = PerevalAdded.objects.all()
    serializer_class = SubmitDataSerializer

    def patch(self, request, *args, **kwargs):
        pereval = self.get_object()

        # 🔹 Проверяем, можно ли редактировать (статус должен быть "New")
        if pereval.status.id != 1:  # ✅ Сравниваем ID, а не строку
            return Response({"status": 400, "message": "Обновление запрещено: статус не new"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Удаляем `user` и `status` из обновляемых данных
        mutable_data = request.data.copy()
        mutable_data.pop("user", None)
        mutable_data.pop("status", None)

        serializer = self.get_serializer(pereval, data=mutable_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "message": "Перевал успешно обновлён"}, status=status.HTTP_200_OK)

        return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SubmitDataListView(ListAPIView):
    """Получение списка всех перевалов."""

    serializer_class = SubmitDataSerializer

    def get_queryset(self):
        """Возвращает все перевалы без фильтрации."""
        return PerevalAdded.objects.all()  # 🔥 Теперь без фильтрации по email


class SubmitDataDetailView(RetrieveAPIView):
    """Получение информации о конкретном перевале"""
    queryset = PerevalAdded.objects.all()
    serializer_class = SubmitDataSerializer


class RegisterView(APIView):
    """Регистрация нового пользователя"""

    @swagger_auto_schema(
        request_body=PerevalUserSerializer,  # Указываем, что в тело запроса вводятся данные пользователя
        # responses={201: openapi.Response("Успешная регистрация", PerevalUserSerializer)},
    )
    def post(self, request):
        """POST-запрос на создание нового пользователя"""
        serializer = PerevalUserSerializer(data=request.data)
        if serializer.is_valid():
            user = DatabaseService.add_user(
                email=serializer.validated_data['email'],
                fam=serializer.validated_data['fam'],
                name=serializer.validated_data['name'],
                otc=serializer.validated_data.get('otc', ''),
                phone=serializer.validated_data['phone']
            )
            return Response({"message": "Пользователь успешно зарегистрирован", "user_id": user.id},
                            status=status.HTTP_201_CREATED)

        return Response({"message": "Ошибка валидации", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class SubmitDataReplaceView(UpdateAPIView):
    """Полное обновление перевала (PUT)"""

    queryset = PerevalAdded.objects.all()
    serializer_class = SubmitDataSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SubmitDataSerializer,  # Запрос с полными данными
        responses={
            200: openapi.Response("Перевал обновлён", SubmitDataSerializer),
            400: "Обновление запрещено: статус не `new`",
            404: "Перевал не найден"
        },
    )
    def put(self, request, pk, *args, **kwargs):
        """Обрабатывает PUT-запрос на полное обновление перевала"""
        user_email = request.user.email  # Берём email из JWT-токена

        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        # 🔒 Проверяем, является ли пользователь автором перевала
        if pereval.user.email != user_email:
            return Response({"state": 0, "message": "Вы не являетесь владельцем этого перевала"},
                            status=status.HTTP_403_FORBIDDEN)

        # Проверяем, можно ли обновлять (только если `new`)
        if pereval.status != "new":
            return Response(
                {"state": 0, "message": "Редактирование запрещено: статус перевала не `new`"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubmitDataSerializer(pereval, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"state": 1, "message": "Перевал успешно обновлён"}, status=status.HTTP_200_OK)

        return Response({"state": 0, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    class SubmitDataDeleteView(APIView):
        """Удаление перевала (DELETE)"""

        @swagger_auto_schema(
            responses={
                200: "Перевал удалён",
                400: "Удаление запрещено: статус не `new`",
                404: "Перевал не найден"
            }
        )
        def delete(self, request, pk, *args, **kwargs):
            """Удаляет перевал, если статус `new`"""
            user_email = request.user.email  # Берём email из JWT-токена

            try:
                pereval = PerevalAdded.objects.get(pk=pk)
            except PerevalAdded.DoesNotExist:
                return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

            # 🔒 Проверяем, является ли пользователь автором перевала
            if pereval.user.email != user_email:
                return Response({"state": 0, "message": "Вы не являетесь владельцем этого перевала"},
                                status=status.HTTP_403_FORBIDDEN)

            if pereval.status != "new":
                return Response(
                    {"state": 0, "message": "Удаление запрещено: статус перевала не `new`"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pereval.delete()
            return Response({"state": 1, "message": "Перевал успешно удалён"}, status=status.HTTP_200_OK)


class SubmitDataDeleteView(APIView):
    """Удаление перевала (DELETE)"""

    @swagger_auto_schema(
        responses={
            200: "Перевал удалён",
            400: "Удаление запрещено: статус не `new`",
            404: "Перевал не найден"
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        """Удаляет перевал, если статус `new`"""
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        if pereval.status != "new":
            return Response(
                {"state": 0, "message": "Удаление запрещено: статус перевала не `new`"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pereval.delete()
        return Response({"state": 1, "message": "Перевал успешно удалён"}, status=status.HTTP_200_OK)


class DeletePerevalPhotoView(APIView):
    """Удаление фотографии перевала (DELETE)"""

    @swagger_auto_schema(
        responses={
            200: "Фотография удалена",
            400: "Удаление запрещено: статус перевала не `new`",
            404: "Фотография или перевал не найдены"
        }
    )
    def delete(self, request, pk, photo_id, *args, **kwargs):
        """Удаляет фотографию, если статус перевала `new`"""
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        if pereval.status != "new":
            return Response(
                {"state": 0, "message": "Удаление запрещено: статус перевала не `new`"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            photo = PerevalImages.objects.get(pk=photo_id, pereval=pereval)
        except PerevalImages.DoesNotExist:
            return Response({"state": 0, "message": "Фотография не найдена"}, status=status.HTTP_404_NOT_FOUND)

        photo.delete()
        return Response({"state": 1, "message": "Фотография успешно удалена"}, status=status.HTTP_200_OK)


class PerevalPhotosListView(APIView):
    """Получение списка фотографий перевала"""

    @swagger_auto_schema(
        responses={200: PerevalImagesSerializer(many=True)},
    )
    def get(self, request, pk, *args, **kwargs):
        """Возвращает список фото для конкретного перевала"""
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        photos = PerevalImages.objects.filter(pereval=pereval)
        serializer = PerevalImagesSerializer(photos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ModerationListView(APIView):
    """Получение списка перевалов на модерацию (GET /api/moderation/)"""

    @swagger_auto_schema(
        responses={200: SubmitDataSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """Возвращает список перевалов со статусом `pending`"""
        perevals = PerevalAdded.objects.filter(status="pending")
        serializer = SubmitDataSerializer(perevals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DecisionPerevalView(APIView):
    """Обрабатывает решения модераторов по перевалам."""
    permission_classes = [IsModerator]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['accepted', 'rejected'])
            },
        ),
        responses={
            200: "Перевал обновлён",
            400: "Некорректный статус или перевал уже обработан",
            404: "Перевал не найден"
        }
    )
    def put(self, request, pk, *args, **kwargs):
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["accepted", "rejected"]:
            return Response({"state": 0, "message": "Некорректный статус"}, status=status.HTTP_400_BAD_REQUEST)

        if pereval.status in ["accepted", "rejected"]:
            return Response({"state": 0, "message": "Перевал уже обработан"}, status=status.HTTP_400_BAD_REQUEST)

        pereval.status = new_status
        pereval.save()
        return Response({"state": 1, "message": f"Перевал {new_status}"}, status=status.HTTP_200_OK)



# class ApprovePerevalView(APIView):
#     """Подтверждение перевала (PUT /api/moderation/{id}/approve/)"""
#
#     @swagger_auto_schema(
#         responses={
#             200: "Перевал подтверждён",
#             404: "Перевал не найден",
#             400: "Перевал уже подтверждён или отклонён"
#         }
#     )
#     def put(self, request, pk, *args, **kwargs):
#         """Устанавливает статус `accepted`"""
#         try:
#             pereval = PerevalAdded.objects.get(pk=pk)
#         except PerevalAdded.DoesNotExist:
#             return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
#
#         if pereval.status != "pending":
#             return Response({"state": 0, "message": "Перевал уже обработан"}, status=status.HTTP_400_BAD_REQUEST)
#
#         pereval.status = "accepted"
#         pereval.save()
#
#         return Response({"state": 1, "message": "Перевал подтверждён"}, status=status.HTTP_200_OK)


# class RejectPerevalView(APIView):
#     """Отклонение перевала (PUT /api/moderation/{id}/reject/)"""
#
#     @swagger_auto_schema(
#         responses={
#             200: "Перевал отклонён",
#             404: "Перевал не найден",
#             400: "Перевал уже подтверждён или отклонён"
#         }
#     )
#     def put(self, request, pk, *args, **kwargs):
#         """Устанавливает статус `rejected`"""
#         try:
#             pereval = PerevalAdded.objects.get(pk=pk)
#         except PerevalAdded.DoesNotExist:
#             return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
#
#         if pereval.status != "pending":
#             return Response({"state": 0, "message": "Перевал уже обработан"}, status=status.HTTP_400_BAD_REQUEST)
#
#         pereval.status = "rejected"
#         pereval.save()
#
#         return Response({"state": 1, "message": "Перевал отклонён"}, status=status.HTTP_200_OK)
#

class SubmitPerevalForModerationView(APIView):
    """Отправка перевала на модерацию (PUT /api/passes/{id}/submit/)"""

    @swagger_auto_schema(
        responses={
            200: "Перевал отправлен на модерацию",
            400: "Перевал уже отправлен или подтверждён",
            404: "Перевал не найден"
        }
    )
    def put(self, request, pk, *args, **kwargs):
        """Меняет статус перевала с `new` на `pending`"""
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        if pereval.status != "new":
            return Response({"state": 0, "message": "Перевал уже отправлен или обработан"},
                            status=status.HTTP_400_BAD_REQUEST)

        pereval.status = "pending"
        pereval.save()

        return Response({"state": 1, "message": "Перевал отправлен на модерацию"}, status=status.HTTP_200_OK)


class ApiSettingsView(RetrieveUpdateAPIView):
    """Управление настройками API (авторизация)"""

    queryset = ApiSettings.objects.all()
    serializer_class = ApiSettingsSerializer  # Создадим этот сериализатор ниже
    permission_classes = [IsAdminUser]  # Только администраторы могут изменять настройку

    def get_object(self):
        """Получаем или создаём объект с настройками API"""
        obj, created = ApiSettings.objects.get_or_create(id=1)  # Убеждаемся, что запись есть
        return obj

    def perform_update(self, serializer):
        """Логируем, кто изменил настройку"""
        instance = serializer.save(updated_by=self.request.user)
        print(f"⚙️ API Authentication изменена: {instance.require_authentication} (by {self.request.user})")


class ModeratorListView(ListCreateAPIView):
    """Управление модераторами"""

    queryset = ModeratorGroup.objects.all()
    permission_classes = [IsSuperAdmin]  # Только супер-админ может управлять модераторами

    def post(self, request, *args, **kwargs):
        """Добавление модератора"""
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            if hasattr(user, "moderator_group"):
                return Response({"error": "Пользователь уже модератор"}, status=status.HTTP_400_BAD_REQUEST)
            ModeratorGroup.objects.create(user=user, added_by=request.user)
            return Response({"message": "Модератор добавлен"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)


class ModeratorDeleteView(DestroyAPIView):
    """Удаление модератора"""

    queryset = ModeratorGroup.objects.all()
    permission_classes = [IsSuperAdmin]  # Только супер-админ может удалять модераторов

    def delete(self, request, *args, **kwargs):
        """Удаление модератора"""
        mod_id = kwargs.get("pk")
        try:
            moderator = ModeratorGroup.objects.get(id=mod_id)
            moderator.delete()
            return Response({"message": "Модератор удалён"}, status=status.HTTP_200_OK)
        except ModeratorGroup.DoesNotExist:
            return Response({"error": "Модератор не найден"}, status=status.HTTP_404_NOT_FOUND)
