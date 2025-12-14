@echo off
echo ▶ Ждём PostgreSQL...
docker compose up -d
timeout /t 10 /nobreak >nul

if not exist venv (
    echo ▶ Создаем виртуальное окружение...
    python -m venv venv
)

call venv\Scripts\activate

echo ▶ Устанавливаем зависимости...
pip install -r requirements.txt

echo ▶ Прогоняем миграции...
python manage.py migrate

echo ▶ Загружаем меню...
python manage.py load_menu

echo ▶ Запускаем сервер...
python manage.py runserver 8000
