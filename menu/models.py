from django.db import models


class Category(models.Model):
    # CharField - это строка (VARCHAR). max_length обязателен.
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="URL-метка")  # например "pizza" для ссылки

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name  # Чтобы в админке писалось "Пицца", а не "Category object (1)"


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание")  # Текст любой длины
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")  # Деньги храним в Decimal!

    # Ссылка на категорию (Один ко многим: в одной категории много товаров)
    # on_delete=models.CASCADE означает: если удалить категорию, удалятся и все товары в ней.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")

    # Картинка. upload_to указывает папку, куда кидать файлы
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото")

    is_available = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('cooking', 'Готовится'),
        ('delivery', 'В пути'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    # Пока не привязываем к User, чтобы было проще тестировать
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # Общая сумма заказа (будем считать её сами)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']  # Сначала новые

    def __str__(self):
        return f"Заказ #{self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент покупки")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"