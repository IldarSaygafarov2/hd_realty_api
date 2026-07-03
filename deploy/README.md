# Деплой на VPS (Docker Compose + nginx на сервере)

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
- `COMPOSE_PROJECT_NAME=hd_realty` — уникальное имя проекта
- `WEB_PORT=8000` — порт, на котором Docker Compose откроет приложение для проксирования nginx

**CSRF и CORS (API Django)** — в `.env` указать домены:
- `CSRF_TRUSTED_ORIGINS=https://ваш-домен.com,http://IP:8080`
- `CORS_ALLOWED_ORIGINS=https://ваш-домен.com,http://фронтенд:5173,...`

Это действует только на ответы **приложения** (REST и т.д.). Файлы **`/media/`** (видео, изображения) отдаёт **nginx**, поэтому для них уже прописаны заголовки CORS в `deploy/nginx-docker.conf` (после правок перезапустите контейнер `nginx`: `docker compose ... restart nginx`). Если медиа отдаёте не из этого образа — продублируйте тот же блок `location /media/` в своём конфиге.

## 3. Запуск

```bash
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

Приложение будет доступно локально на `http://127.0.0.1:8000` (или порт из `WEB_PORT`), а nginx на сервере будет проксировать внешний трафик на него. В `ALLOWED_HOSTS` добавьте IP и домен.

Важно: для общих статических файлов и медиа используйте путь вне `/root`, например `/var/www/hd_realty/...`, потому что nginx-процесс не может читать файлы из `/root`. Также в конфиге обязательно укажите ваш реальный домен в `server_name`.

## 4. Администратор

```bash
docker compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```
