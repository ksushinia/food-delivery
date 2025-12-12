from django.urls import path
from .views import ProductListView, CategoryListView, CreateOrderView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('orders/', CreateOrderView.as_view(), name='create-order'),
]