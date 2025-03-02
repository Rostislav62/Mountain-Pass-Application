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
from main.models import PerevalImages, PerevalStatus
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.generics import ListAPIView  # Импортируем базовый класс для списков
from rest_framework import status  # Для указания HTTP-статусов
from main.models import PerevalAdded  # Импортируем модель Перевала
from main.serializers import SubmitDataSerializer  # Подключаем сериализатор
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

    # def get(self, request):
    #     """📌 GET: Получает список перевалов пользователя по email"""
    #     email = request.query_params.get("user__email")
    #
    #     if not email:
    #         return Response({"message": "Требуется email"}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     perevals = PerevalAdded.objects.filter(user__email=email)
    #     serializer = SubmitDataSerializer(perevals, many=True)
    #
    #     return Response(serializer.data, status=status.HTTP_200_OK)



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


class SubmitDataUpdateView(UpdateAPIView):
    """Редактирование данных о перевале, если статус new"""

    queryset = PerevalAdded.objects.all()
    serializer_class = SubmitDataSerializer
    http_method_names = ['patch']  # ❗ Оставляем только PATCH, убираем PUT

    def patch(self, request, *args, **kwargs):
        pereval = self.get_object()  # 🔹 Получаем объект перевала по ID

        # 🔹 Проверяем, можно ли редактировать (статус должен быть "New")
        if pereval.status.id != 1:  # ✅ Сравниваем ID, а не строку
            return Response(
                {"status": 400, "message": "Обновление запрещено: статус не new"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Получаем данные из запроса и оставляем только нужные поля
        mutable_data = request.data.copy()

        # Оставляем только разрешенные поля
        allowed_fields = ["beautyTitle", "title", "other_titles", "coord", "difficulties"]

        # 🔹 Убираем все другие поля, кроме разрешенных
        filtered_data = {key: mutable_data[key] for key in allowed_fields if key in mutable_data}

        # 🔹 Проверяем, что в `coord` переданы только корректные данные (latitude, longitude, height)
        if "coord" in filtered_data:
            coord_fields = ["latitude", "longitude", "height"]
            filtered_data["coord"] = {k: v for k, v in filtered_data["coord"].items() if k in coord_fields}

        # 🔹 Проверяем, что в `difficulties` передан корректный формат
        if "difficulties" in filtered_data and isinstance(filtered_data["difficulties"], list):
            for diff in filtered_data["difficulties"]:
                diff_keys = ["season", "difficulty"]
                for key in list(diff.keys()):
                    if key not in diff_keys:
                        del diff[key]  # Удаляем лишние поля из вложенного словаря

        # 🔹 Применяем обновления только с указанными полями
        serializer = self.get_serializer(pereval, data=filtered_data, partial=True)

        if serializer.is_valid():
            serializer.save()  # 🔹 Сохраняем обновленные данные
            return Response({"status": 200, "message": "Перевал успешно обновлён"}, status=status.HTTP_200_OK)

        return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



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
            user = DatabaseService.add_user(
                email=serializer.validated_data['email'],
                family_name=serializer.validated_data['family_name'],
                first_name=serializer.validated_data['first_name'],
                father_name=serializer.validated_data.get('father_name', ''),
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

    permission_classes = [IsAuthenticated]  # Удалять могут только авторизованные пользователи

    @swagger_auto_schema(
        responses={
            200: "Перевал удалён",
            400: "Удаление запрещено: статус не `new`",
            403: "Нет прав на удаление",
            404: "Перевал не найден"
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        """
        Удаляет перевал, если статус `new`
        ✅ Админ (`IsSuperAdmin`) может удалять всё.
        ✅ Модератор (`IsModerator`) может удалять, только если статус `new`.
        ✅ Обычный пользователь может удалить свой перевал, пока он в статусе `new`.
        """

        try:
            pereval = PerevalAdded.objects.get(pk=pk)
        except PerevalAdded.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Администратор может удалить любой перевал без ограничений
        if request.user.is_superuser:
            pereval.delete()
            return Response({"state": 1, "message": "Перевал удалён администратором"}, status=status.HTTP_200_OK)

        # ✅ Проверяем, является ли пользователь автором перевала
        if pereval.user.email == request.user.email:
            if pereval.status.id == 1:  # Статус "new"
                pereval.delete()
                return Response({"state": 1, "message": "Перевал удалён пользователем"}, status=status.HTTP_200_OK)
            else:
                return Response({"state": 0, "message": "Вы не можете удалить перевал с текущим статусом"},
                                status=status.HTTP_400_BAD_REQUEST)

        # ✅ Проверяем, является ли пользователь модератором
        if hasattr(request.user, "moderator_group"):  # Проверяем, является ли пользователь модератором
            if pereval.status.id == 1:  # Статус "new"
                pereval.delete()
                return Response({"state": 1, "message": "Перевал удалён модератором"}, status=status.HTTP_200_OK)
            else:
                return Response({"state": 0, "message": "Модератор может удалить только перевалы со статусом `new`"},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"state": 0, "message": "У вас нет прав на удаление этого перевала"},
                        status=status.HTTP_403_FORBIDDEN)


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

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="📌 Удаление фотографии перевала",
        responses={
            200: "Фотография удалена",
            403: "Нет прав на удаление",
            404: "Фотография не найдена"
        }
    )
    def delete(self, request, photo_id, *args, **kwargs):
        """Удаляет фотографию, если у пользователя есть права"""
        logger.info(f"🚀 DELETE /uploadImage/{photo_id}/ вызван")

        try:
            photo = PerevalImages.objects.get(pk=photo_id)
        except PerevalImages.DoesNotExist:
            logger.warning(f"❌ Фотография {photo_id} не найдена")
            return Response({"state": 0, "message": "Фотография не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Проверяем, является ли пользователь автором перевала
        if request.user.is_superuser or photo.pereval.user.email == request.user.email:
            photo.delete()
            logger.info(f"✅ Фотография {photo_id} удалена пользователем {request.user.email}")
            return Response({"state": 1, "message": "Фотография удалена"}, status=status.HTTP_200_OK)

        logger.warning(f"⛔ У пользователя {request.user.email} нет прав на удаление {photo_id}")
        return Response({"state": 0, "message": "У вас нет прав на удаление этой фотографии"},
                        status=status.HTTP_403_FORBIDDEN)




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
        return Response({"state": 1, "message": f"Перевал обновлён до статуса ID {status_id}"}, status=status.HTTP_200_OK)




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
