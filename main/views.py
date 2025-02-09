#  /Mountain Pass Application/main/views.py

import traceback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from main.serializers import SubmitDataSerializer
from main.db_service import DatabaseService
from django.core.exceptions import ObjectDoesNotExist

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
