from rest_framework import serializers
from .models import Product, Category, Order, OrderItem
from django.db import transaction
from rest_framework.exceptions import ValidationError

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available']

class CategorySerializer(serializers.ModelSerializer):
    # Вкладываем продукты внутрь категории (опционально, но удобно)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Вложенный список товаров

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'phone_number', 'address', 'total_price', 'items']
        read_only_fields = ['total_price']  # Цену считает сервер, а не юзер

    # ПЕРЕОПРЕДЕЛЯЕМ метод create, чтобы сохранить и заказ, и товары
    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Вытаскиваем товары из данных

        # 1. Создаем сам заказ
        order = Order.objects.create(**validated_data)

        total_price = 0

        # 2. Проходимся по товарам и создаем OrderItem
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price  # Берем цену из базы товаров

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            total_price += price * quantity

        # 3. Обновляем общую стоимость заказа
        order.total_price = total_price
        order.save()

        return order


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'phone_number', 'address', 'total_price', 'items']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # transaction.atomic() гарантирует: либо выполнится ВСЁ, либо НИЧЕГО.
        # Если произойдет ошибка посередине, заказ не создастся.
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total_price = 0

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                # --- ЗАЩИТА ОТ ГОНКИ (select_for_update) ---
                # Мы блокируем строку товара в БД, пока транзакция не закончится.
                # Другой пользователь будет ждать, пока мы не закончим.
                product = Product.objects.select_for_update().get(id=product.id)

                if product.is_available:  # Тут можно добавить проверку количества (stock > 0)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    total_price += product.price * quantity
                else:
                    raise ValidationError(f"Товар {product.name} закончился :(")

            order.total_price = total_price
            order.save()

        return order