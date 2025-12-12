from rest_framework import generics
from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer, OrderCreateSerializer

from rest_framework.permissions import AllowAny
from django.shortcuts import render, get_object_or_404

# Ручка 1: Получить список всех товаров
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer

# Ручка 2: Получить список категорий (с продуктами внутри)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [AllowAny]  # Разрешить всем (даже анонимам)
    authentication_classes = []

# HTML: Главная
def index(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'index.html', {'products': products})

# HTML: Страница заказа
def order_detail(request, pk):
    # Ищем заказ по ID (pk), если нет - 404 ошибка
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order})