from django.urls import include, path
from rest_framework import routers


api_v1_patterns = []

urlpatterns = [
    path('v1/', include(api_v1_patterns))
]