from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menu.views import index, order_detail

urlpatterns = [
    path('admin/', admin.site.urls),

    # Все адреса из приложения menu будут начинаться с /api/
    path('api/', include('menu.urls')),
    path('', index, name='index'),
    path('order/<int:pk>/', order_detail, name='order_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)