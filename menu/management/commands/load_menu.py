import requests
import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from menu.models import Category, Product  # Импортируем твои модели


class Command(BaseCommand):
    help = 'Загружает реальные данные из TheMealDB API'

    def handle(self, *args, **kwargs):
        # 1. Ссылка на API (получить список блюд)
        # Мы берем поиск по букве 'b' (Burgers, Beef...), чтобы получить список популярных
        url = "https://www.themealdb.com/api/json/v1/1/search.php?s="

        self.stdout.write("Начинаю загрузку данных...")

        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка подключения к API: {e}"))
            return

        meals = data.get('meals')
        if not meals:
            self.stdout.write(self.style.WARNING("API не вернуло данных"))
            return

        for meal in meals:
            # Данные из API
            category_name = meal.get('strCategory', 'Разное')
            meal_name = meal.get('strMeal')
            image_url = meal.get('strMealThumb')

            # 2. Создаем или получаем Категорию
            # slugify превращает "Beef & Pork" в "beef-pork" для URL
            cat_slug = slugify(category_name)

            category, created = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': category_name}
            )

            if created:
                self.stdout.write(f"Создана категория: {category_name}")

            # 3. Создаем Товар (если такого еще нет)
            if not Product.objects.filter(name=meal_name).exists():
                # Генерируем случайную цену (в API цен нет)
                price = random.randint(300, 1500)

                product = Product(
                    name=meal_name,
                    description=f"Вкуснейшее блюдо из категории {category_name}. Попробуйте!",
                    price=price,
                    category=category,
                    is_available=True
                )

                # 4. Скачиваем картинку
                if image_url:
                    try:
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            # Сохраняем файл прямо в поле модели
                            file_name = f"{slugify(meal_name)}.jpg"
                            product.image.save(file_name, ContentFile(img_response.content), save=False)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Не удалось скачать картинку для {meal_name}"))

                product.save()
                self.stdout.write(self.style.SUCCESS(f" + Добавлено блюдо: {meal_name} ({price} р.)"))
            else:
                self.stdout.write(f" - Блюдо {meal_name} уже есть в базе")

        self.stdout.write(self.style.SUCCESS("ЗАГРУЗКА ЗАВЕРШЕНА! 🚀"))