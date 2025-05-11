# Фудграм: Сервис для публикации рецептов

Фудграм — это платформа, где пользователи могут публиковать свои кулинарные рецепты, добавлять рецепты других пользователей в избранное и формировать список покупок на основе выбранных рецептов.

## Стек технологий

*   **Бэкенд:** Python, Django, Django REST framework
*   **Фронтенд:** React (предоставляется готовая сборка)
*   **База данных:** PostgreSQL
*   **Веб-сервер/Прокси:** Nginx
*   **Контейнеризация:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions

## Как запустить проект локально (с использованием Docker)

### 1. Предварительные требования

*   Установленный [Docker](https://www.docker.com/get-started)
*   Установленный [Docker Compose](https://docs.docker.com/compose/install/) (обычно идет вместе с Docker Desktop)
*   Система контроля версий [Git](https://git-scm.com/downloads)

### 2. Клонирование репозитория

Откройте терминал или командную строку и выполните:

```bash
git clone https://github.com/Instmois/foodgram-st.git
cd foodgram-st
```

### 3. Создание файла переменных окружения .env

В корневой папке проекта (там же, где находится этот README.md файл и папки backend, frontend, infra) создайте файл с именем .env.
Скопируйте в него следующее содержимое. Для локального запуска эти значения подходят.
```dotenv
# .env (в корне проекта)

# Настройки базы данных PostgreSQL
POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password # Рекомендуется сменить на более сложный пароль

# Настройки Django
DJANGO_SECRET_KEY='your_very_secret_django_key_for_development_12345' # ЗАМЕНИТЕ ЭТО НА СВОЙ УНИКАЛЬНЫЙ КЛЮЧ
DEBUG=True # True для разработки, False для продакшена

# Хосты, с которых разрешены запросы (для Django)
# Для Docker и локального доступа этого обычно достаточно
ALLOWED_HOSTS=localhost,127.0.0.1,backend 

# Настройки подключения к БД из Django (используются в settings.py)
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db # Имя сервиса PostgreSQL в docker-compose.yml
DB_PORT=5432
# DB_NAME, DB_USER, DB_PASSWORD берутся из переменных POSTGRES_* выше
```

Важно:
Замените значение DJANGO_SECRET_KEY на свой собственный уникальный и сложный ключ. Вы можете сгенерировать его, например, так (в Python консоли):
```bash
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. Сборка и запуск контейнеров
Перейдите в папку infra и выполните команду для сборки образов и запуска всех сервисов:
```bash 
cd infra
docker-compose up --build
```

### 5. Доступ к приложению
После успешного запуска сервисов, приложение будет доступно по следующим адресам:
- Основной сайт (фронтенд): http://localhost/ или http://127.0.0.1/
- Административная панель Django: http://localhost/admin/
- Документация API (Redoc): http://localhost/api/docs/
- API эндпоинты: http://localhost/api/... (например, http://localhost/api/recipes/)