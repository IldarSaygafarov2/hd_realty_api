# Деплой на VPS (Docker, nginx в контейнере)

## 1. Подготовка

```bash
cd /opt
git clone <repo> hd_realty
cd hd_realty
```

## 2. Настройка .env

```bash
cp .env.production.dist .env
nano .env  # SECRET_KEY, ALLOWED_HOSTS, DB_PASSWORD
```

**Если на сервере уже запущен другой проект (nginx на 80):**
- `NGINX_HTTP_PORT=8080` — приложение будет на порту 8080
- `COMPOSE_PROJECT_NAME=hd_realty` — уникальное имя проекта

## 3. Запуск

```bash
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

Приложение: `http://IP_сервера:8080` (или порт из NGINX_HTTP_PORT). В ALLOWED_HOSTS добавить IP и домен.

## 4. Администратор

```bash
docker compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```
