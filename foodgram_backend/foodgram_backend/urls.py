from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            'redoc/',
            TemplateView.as_view(template_name='redoc.html'),
            name='redoc'
        ),
    ]
