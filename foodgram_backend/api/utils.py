from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            response.data['detail'] = 'Ошибка 404 - страница не найдена!'

    return response
