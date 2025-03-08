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
from main.models import PerevalImages, PerevalStatus, PerevalUser, EmailConfirmationToken
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.generics import ListAPIView  # Импортируем базовый класс для списков
from rest_framework import status  # Для указания HTTP-статусов
from main.models import PerevalAdded  # Импортируем модель Перевала
from main.serializers import SubmitDataSerializer, PerevalUserCheckSerializer, \
    PerevalUserUpdateSerializer  # Подключаем сериализатор
from drf_yasg.utils import swagger_auto_schema  # 📌 Импортируем Swagger-декоратор Swagger-документация
from drf_yasg import openapi  # 📌 Импортируем для описания параметров
from rest_framework.parsers import MultiPartParser, FormParser  # 📌 Добавляем поддержку загрузки файлов
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
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
from rest_framework.permissions import IsAuthenticated
from main.utils import send_confirmation_email
from .serializers import PerevalAddedSerializer


# Настроим логгер
logger = logging.getLogger(__name__)


class SubmitDataView(APIView):
    """API для приёма и получения данных о перевале"""

    @swagger_auto_schema(
        request_body=SubmitDataSerializer,  # 📌 Позволяет вводить JSON в Swagger
        manual_parameters=[],  # 📌 Убирает ненужные параметры в UI
        responses={201: openapi.Response("Created", SubmitDataSerializer)},  # 📌 Описывает успешный ответ
    )
    def post(self, request):
        """📌 POST: Создаёт новый перевал"""
        logger.info("🚀 ШАГ 1: Получен POST-запрос на /submitData/")
        print("📥 ШАГ 1: Полученные данные:", request.data)

        try:
            serializer = SubmitDataSerializer(data=request.data)

            if serializer.is_valid():
                data = serializer.validated_data
                logger.info("✅ ШАГ 2: Данные успешно валидированы")
                print("✅ ШАГ 2: Валидированные данные:", data)

                # 🔹 Создаём или получаем пользователя
                logger.info("🔍 ШАГ 3: Вызов `add_user()` для создания/поиска пользователя")
                user = DatabaseService.add_user(data["user"])

                logger.info(f"👤 ШАГ 4: Пользователь найден/создан: {user}")
                print(f"👤 ШАГ 4: Пользователь найден/создан: {user}")

                # 🔹 Проверка условия `connect`
                if not data.get("connect", False):
                    logger.warning("❌ ШАГ 5: Нет связи, перевал не будет отправлен")
                    return Response(
                        {"status": 400, "message": "Нет связи. Перевал нельзя отправить."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 🔹 Создаём перевал
                logger.info(f"🏔️ ШАГ 6: Вызов `add_pereval()` для создания перевала (user_id={user.id})")
                pereval = DatabaseService.add_pereval(user_email=user.email, data=data)

                logger.info(f"✅ ШАГ 7: Перевал успешно создан, ID: {pereval.id}")
                print(f"✅ ШАГ 7: Перевал успешно создан, ID: {pereval.id}")

                return Response({"status": 200, "message": None, "id": pereval.id}, status=status.HTTP_201_CREATED)

            logger.warning(f"❌ ШАГ 8: Ошибка валидации: {serializer.errors}")
            return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"⚠ ШАГ 9: Ошибка сервера: {str(e)}")
            traceback.print_exc()
            return Response({"status": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class SubmitDataUpdateView(APIView):
    """Редактирование данных о перевале, если статус new и пользователь является автором"""

    http_method_names = ['patch']  # Оставляем только PATCH

    @swagger_auto_schema(
        operation_description="Обновляет перевал, если email совпадает и статус new",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],  # Email обязателен
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя'),
                'beautyTitle': openapi.Schema(type=openapi.TYPE_STRING, description='Название горного массива'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название перевала'),
                'other_titles': openapi.Schema(type=openapi.TYPE_STRING, description='Другие названия'),
                'coord': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='Широта'),
                        'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='Долгота'),
                        'height': openapi.Schema(type=openapi.TYPE_NUMBER, description='Высота')
                    }
                ),
                'difficulties': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'season': openapi.Schema(type=openapi.TYPE_INTEGER, description='Сезон'),
                            'difficulty': openapi.Schema(type=openapi.TYPE_INTEGER, description='Сложность')
                        }
                    )
                )
            }
        ),
        responses={
            200: openapi.Response('Перевал успешно обновлён', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'state': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Перевал успешно обновлён')
                }
            )),
            400: 'Ошибка валидации или статус не new',
            403: 'Нет прав на редактирование',
            404: 'Перевал не найден'
        }
    )
    def patch(self, request, pk, *args, **kwargs):
        """Обновляет перевал, если email совпадает и статус new"""
        # Получаем объект перевала по ID
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response(
                {"state": 0, "message": "Перевал не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие email в теле запроса
        email = request.data.get("email")
        if not email:
            return Response(
                {"state": 0, "message": "Поле email обязательно"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, является ли пользователь автором перевала
        if pereval.user.email != email:
            return Response(
                {"state": 0, "message": "У вас нет прав на редактирование этого перевала"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем, что статус new (id = 1)
        if pereval.status.id != 1:
            return Response(
                {"state": 0, "message": "Обновление запрещено: статус не new"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем данные из запроса и фильтруем только разрешённые поля
        mutable_data = request.data.copy()
        allowed_fields = ["beautyTitle", "title", "other_titles", "coord", "difficulties"]
        filtered_data = {key: mutable_data[key] for key in allowed_fields if key in mutable_data}

        # Фильтруем координаты
        if "coord" in filtered_data:
            coord_fields = ["latitude", "longitude", "height"]
            filtered_data["coord"] = {k: v for k, v in filtered_data["coord"].items() if k in coord_fields}

        # Фильтруем сложности
        if "difficulties" in filtered_data and isinstance(filtered_data["difficulties"], list):
            for diff in filtered_data["difficulties"]:
                diff_keys = ["season", "difficulty"]
                for key in list(diff.keys()):
                    if key not in diff_keys:
                        del diff[key]

        # Сериализуем и сохраняем данные
        serializer = SubmitDataSerializer(pereval, data=filtered_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"state": 1, "message": "Перевал успешно обновлён"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"state": 0, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubmitDataListView(ListAPIView):
    """Получение списка всех перевалов."""

    serializer_class = SubmitDataSerializer

    def get_queryset(self):
        """Возвращает все перевалы без фильтрации."""
        return PerevalAdded.objects.all()  # 🔥 Теперь без фильтрации по email


class SubmitDataDetailView(APIView):
    """Получение информации о конкретном перевале"""

    def get(self, request, pk, *args, **kwargs):
        """
        ✅ Получение информации о конкретном перевале по ID.
        ✅ Если перевал не найден, возвращаем кастомное сообщение.
        """
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
            serializer = SubmitDataSerializer(pereval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PerevalAdded.DoesNotExist:
            return Response(
                {"state": 0, "message": f"Перевал с ID {pk} не найден"},
                status=status.HTTP_404_NOT_FOUND
            )


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
            user_data = {
                "email": serializer.validated_data["email"],
                "family_name": serializer.validated_data["family_name"],
                "first_name": serializer.validated_data["first_name"],
                "father_name": serializer.validated_data.get("father_name", ""),
                "phone": serializer.validated_data["phone"]
            }

            user = DatabaseService.add_user(user_data)
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
        operation_description="Удаляет перевал, если email совпадает и статус new",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя')
            }
        ),
        responses={
            200: openapi.Response('Перевал удалён', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'state': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Перевал удалён')
                }
            )),
            400: 'Удаление запрещено: статус не new',
            403: 'Нет прав на удаление',
            404: 'Перевал не найден'
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        """Удаляет перевал, если email совпадает и статус new"""
        logger.info(f"🚀 DELETE /submitData/{pk}/ вызван")

        # Получаем перевал по ID
        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            logger.warning(f"❌ Перевал {pk} не найден")
            return Response(
                {"state": 0, "message": "Перевал не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие email в теле запроса
        email = request.data.get("email")
        if not email:
            logger.warning("❌ Поле email отсутствует в запросе")
            return Response(
                {"state": 0, "message": "Поле email обязательно"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, является ли пользователь автором перевала
        if pereval.user.email != email:
            logger.warning(f"⛔ У пользователя {email} нет прав на удаление перевала {pk}")
            return Response(
                {"state": 0, "message": "У вас нет прав на удаление этого перевала"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем, что статус new (id = 1)
        if pereval.status.id != 1:
            logger.warning(f"❌ Удаление запрещено: статус перевала {pk} не new")
            return Response(
                {"state": 0, "message": "Удаление запрещено: статус не new"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаляем перевал
        pereval.delete()
        logger.info(f"✅ Перевал {pk} удалён пользователем {email}")
        return Response(
            {"state": 1, "message": "Перевал удалён"},
            status=status.HTTP_200_OK
        )


class PerevalPhotosListView(APIView):
    """Получение списка фотографий перевала"""

    def get(self, request, pk, *args, **kwargs):
        """Возвращает список фотографий для перевала"""
        logger.info(f"🚀 GET /uploadImage/photos/{pk}/ вызван")

        try:
            photos = PerevalImages.objects.filter(pereval_id=pk)
            if not photos.exists():
                logger.warning(f"❌ Фотографии для перевала {pk} не найдены")
                return Response({"state": 0, "message": "Фотографии не найдены"}, status=status.HTTP_404_NOT_FOUND)

            photos_data = [{"id": photo.id, "file_name": photo.data, "title": photo.title} for photo in photos]

            logger.info(f"✅ Найдено {len(photos_data)} фотографий для перевала {pk}")
            return Response({"state": 1, "photos": photos_data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"⚠ Ошибка при получении фотографий перевала {pk}: {str(e)}")
            return Response({"state": 0, "message": "Ошибка сервера"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeletePerevalPhotoView(APIView):
    """Удаление фотографии перевала"""

    @swagger_auto_schema(
        operation_description="📌 Удаление фотографии перевала, если email совпадает и статус new",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя')
            }
        ),
        responses={
            200: openapi.Response('Фотография удалена', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'state': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Фотография удалена')
                }
            )),
            400: 'Удаление запрещено: статус не new',
            403: 'Нет прав на удаление',
            404: 'Фотография не найдена'
        }
    )
    def delete(self, request, photo_id, *args, **kwargs):
        """Удаляет фотографию, если email совпадает и статус new"""
        logger.info(f"🚀 DELETE /uploadImage/{photo_id}/ вызван")

        # Получаем фотографию по ID
        try:
            photo = PerevalImages.objects.get(pk=photo_id)
        except PerevalImages.DoesNotExist:
            logger.warning(f"❌ Фотография {photo_id} не найдена")
            return Response(
                {"state": 0, "message": "Фотография не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие email в теле запроса
        email = request.data.get("email")
        if not email:
            logger.warning("❌ Поле email отсутствует в запросе")
            return Response(
                {"state": 0, "message": "Поле email обязательно"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, является ли пользователь автором перевала
        if photo.pereval.user.email != email:
            logger.warning(f"⛔ У пользователя {email} нет прав на удаление {photo_id}")
            return Response(
                {"state": 0, "message": "У вас нет прав на удаление этой фотографии"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем, что статус перевала new (id = 1)
        if photo.pereval.status.id != 1:
            logger.warning(f"❌ Удаление запрещено: статус перевала не new для фото {photo_id}")
            return Response(
                {"state": 0, "message": "Удаление запрещено: статус перевала не new"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаляем фотографию
        photo.delete()
        logger.info(f"✅ Фотография {photo_id} удалена пользователем {email}")
        return Response(
            {"state": 1, "message": "Фотография удалена"},
            status=status.HTTP_200_OK
        )


class ModerationListView(APIView):
    """Получение списка перевалов на модерацию (GET /api/moderation/)"""

    @swagger_auto_schema(
        responses={200: SubmitDataSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """Возвращает список перевалов со статусом `pending`"""
        PENDING_STATUS_ID = 2  # ✅ ID статуса "pending" в БД
        perevals = PerevalAdded.objects.filter(status=PENDING_STATUS_ID)

        serializer = SubmitDataSerializer(perevals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DecisionPerevalView(APIView):
    """Обрабатывает решения модераторов по перевалам."""
    permission_classes = [IsModerator]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status_id'],
            properties={
                'status_id': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[3, 4])
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

        status_id = request.data.get("status_id")
        if status_id not in [3, 4]:
            return Response({"state": 0, "message": "Некорректный ID статуса"}, status=status.HTTP_400_BAD_REQUEST)

        if pereval.status.id in [3, 4]:
            return Response({"state": 0, "message": "Перевал уже обработан"}, status=status.HTTP_400_BAD_REQUEST)

        pereval.status = PerevalStatus.objects.get(id=status_id)
        pereval.save()
        return Response({"state": 1, "message": f"Перевал обновлён до статуса ID {status_id}"},
                        status=status.HTTP_200_OK)


class SubmitPerevalForModerationView(APIView):
    """Отправка перевала на модерацию (PUT /api/passes/{id}/submit/)"""

    @swagger_auto_schema(
        responses={
            200: "Перевал отправлен на модерацию",
            400: "Перевал уже отправлен на проверку, принят или отклонен",
            404: "Перевал не найден"
        }
    )
    def put(self, request, pk, *args, **kwargs):
        """
        Меняет статус перевала с `new` (ID=1) на `pending` (ID=2).
        Если перевал уже `pending` (ID=2) → сообщение, что он уже отправлен.
        Если перевал `accepted` (ID=3) или `rejected` (ID=4) → сообщение, что он обработан.
        """
        try:
            # 🔍 Ищем перевал по ID
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            # ❌ Если перевал не найден, возвращаем 404
            return Response(
                {"state": 0, "message": "Перевал не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🆔 Получаем ID текущего статуса перевала
        status_id = pereval.status.id

        # ✅ Если статус "New" (ID = 1), меняем его на "Pending" (ID = 2)
        if status_id == 1:
            pereval.status_id = 2
            pereval.save()
            return Response(
                {"state": 1, "message": "Перевал отправлен на модерацию"},
                status=status.HTTP_200_OK
            )

        # ⚠ Если статус уже "Pending" (ID = 2)
        elif status_id == 2:
            return Response(
                {"state": 0, "message": "Перевал уже отправлен на проверку"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Если статус "Accepted" (ID = 3)
        elif status_id == 3:
            return Response(
                {"state": 0, "message": "Перевал уже был принят модератором"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ❌ Если статус "Rejected" (ID = 4)
        elif status_id == 4:
            return Response(
                {"state": 0, "message": "Перевал был отклонен модератором"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔄 На случай, если появятся новые статусы
        return Response(
            {"state": 0, "message": f"Неизвестный статус перевала: {status_id}"},
            status=status.HTTP_400_BAD_REQUEST
        )


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


class UserDetailView(APIView):
    """Получение данных пользователя по email"""

    @swagger_auto_schema(
        operation_description="📌 Получение данных пользователя по email",
        responses={200: PerevalUserCheckSerializer, 404: "Пользователь не найден"}
    )
    def get(self, request, email):
        """Возвращает информацию о пользователе по email"""
        user = PerevalUser.objects.filter(email=email).first()
        if not user:
            return Response({"status": 404, "message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PerevalUserCheckSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestUserUpdateView(APIView):
    """Запрос на изменение данных (отправка кода на email)"""

    def post(self, request, email):
        """Отправляет код подтверждения на email"""
        user = PerevalUser.objects.filter(email=email).first()
        if not user:
            return Response({"status": 404, "message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        send_confirmation_email(user)
        return Response({"status": 200, "message": "Код подтверждения отправлен на email"}, status=status.HTTP_200_OK)


class ConfirmUserUpdateView(APIView):
    """Обновление данных пользователя после подтверждения кода"""

    def patch(self, request, email):
        """Обновляет данные пользователя, если код подтверждения верный"""

        # 🔹 ШАГ 1: Ищем пользователя по email
        user = PerevalUser.objects.filter(email=email).first()
        if not user:
            return Response(
                {"status": 404, "message": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔹 ШАГ 2: Проверяем, передан ли код подтверждения
        code = request.data.get("code")
        if not code:
            return Response(
                {"status": 400, "message": "Код подтверждения обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 ШАГ 3: Ищем код подтверждения в базе
        token = EmailConfirmationToken.objects.filter(user=user, code=code).first()
        if not token:
            return Response(
                {"status": 400, "message": "Неверный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 ШАГ 4: Обновляем данные пользователя
        serializer = PerevalUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # ✅ ШАГ 5: Удаляем использованный код подтверждения
            token.delete()

            return Response(
                {"status": 200, "message": "Данные успешно обновлены"},
                status=status.HTTP_200_OK
            )

        # 🔹 ШАГ 6: Если данные некорректны, возвращаем ошибки
        return Response(
            {"status": 400, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSubmitsView(APIView):
    """Получение всех перевалов конкретного пользователя по email"""

    def get(self, request, email):
        """
        Возвращает список перевалов пользователя по его email.
        Если перевалов нет, сообщает, что записей не найдено.
        """
        user = PerevalUser.objects.filter(email=email).first()
        if not user:
            return Response({"status": 404, "message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        submits = PerevalAdded.objects.filter(user=user)
        if not submits.exists():
            return Response({"status": 200, "message": "У пользователя пока нет записанных перевалов"}, status=status.HTTP_200_OK)

        serializer = PerevalAddedSerializer(submits, many=True)
        return Response({"status": 200, "data": serializer.data}, status=status.HTTP_200_OK)
