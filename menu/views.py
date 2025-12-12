from rest_framework import generics
from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer, OrderCreateSerializer
from django.shortcuts import render
from rest_framework.permissions import AllowAny

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

def index(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'index.html', {'products': products})