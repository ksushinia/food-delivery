from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Product, Category, Order, OrderItem, PromoCode


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available']


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # Вот оно - поле, которое принимает код, но не пишет его в базу напрямую
    promo_code_str = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'phone_number', 'address', 'total_price', 'items', 'promo_code_str']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Вытаскиваем код
        promo_code_input = validated_data.pop('promo_code_str', None)

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total_price = 0

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                # Защита от гонки
                product = Product.objects.select_for_update().get(id=product.id)

                if product.is_available:
                    OrderItem.objects.create(
                        order=order, product=product, quantity=quantity, price=product.price
                    )
                    total_price += product.price * quantity
                else:
                    raise ValidationError(f"Товар {product.name} закончился :(")

            # --- Логика скидки ---
            if promo_code_input:
                try:
                    # Ищем купон (iexact = не важно, большие или маленькие буквы)
                    coupon = PromoCode.objects.get(code__iexact=promo_code_input)

                    if coupon.is_valid():
                        discount = (total_price * coupon.discount_percent) / 100
                        print(f"СКИДКА ПРИМЕНЕНА: {discount} руб.")
                        total_price -= discount
                        order.promo_code = coupon.code
                    else:
                        print("КУПОН ПРОСРОЧЕН")
                except PromoCode.DoesNotExist:
                    print(f"КУПОН '{promo_code_input}' НЕ НАЙДЕН")

            order.total_price = total_price
            order.save()

        return order