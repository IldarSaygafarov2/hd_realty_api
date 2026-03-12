# Деплой на VPS

## 1. Подготовка сервера

```bash
# Установить Docker и Docker Compose
# Клонировать проект в /opt/hd_realty
cd /opt
git clone <repo> hd_realty
cd hd_realty
```

## 2. Настройка окружения

```bash
cp .env.production.dist .env
nano .env  # Заполнить SECRET_KEY, ALLOWED_HOSTS, DB_PASSWORD
```

**Несколько проектов на одном сервере.** Если порты заняты, задайте в `.env`:
- `COMPOSE_PROJECT_NAME=hd_realty` (уникальное имя)
- `WEB_PORT=8001` (если 8000 занят)
- `DB_HOST_PORT=5433` (если 5432 занят; `DB_PORT` оставить 5432 — это порт внутри Docker)

## 3. Запуск приложения

```bash
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

## 4. Nginx на хосте

Скопировать `deploy/nginx.conf.example` в `/etc/nginx/sites-available/hd_realty`, подставить свой домен, путь к проекту (например `/opt/hd_realty`).

```bash
sudo ln -s /etc/nginx/sites-available/hd_realty /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 5. Создание администратора

```bash
docker compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```
