from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menu.views import index

urlpatterns = [
    path('admin/', admin.site.urls),

    # Все адреса из приложения menu будут начинаться с /api/
    path('api/', include('menu.urls')),
    path('', index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)