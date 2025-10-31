# Task Manager API (MVP)

Минимально жизнеспособная система управления проектами и задачами на Django REST Framework.

Документация: http://localhost/redoc/ (или откройте /redoc/ локально). OpenAPI находится в `project_manager/static/redoc.yaml`.

## Возможности
- Проекты: список и создание.
- Задачи в проекте: список и создание.
- Задачи: частичное редактирование по id.
- JWT-аутентификация: регистрация по e-mail/username и получение токена.

Эндпоинты:
- GET /api/v1/projects/
- POST /api/v1/projects/
- GET /api/v1/projects/{id}/tasks/
- POST /api/v1/projects/{id}/tasks/
- PATCH /api/v1/tasks/{id}/

## Технологии
- Python 3.7
- Django 2.2.x
- DRF 3.12.x
- Simple JWT
- Docker, docker-compose, Nginx, Gunicorn

## Запуск через Docker
1) Соберите и запустите контейнеры:
```
 docker-compose up -d --build
```
2) Примените миграции, создайте суперпользователя и соберите статику:
```
 docker-compose exec web python manage.py migrate
 docker-compose exec web python manage.py createsuperuser
 docker-compose exec web python manage.py collectstatic --no-input
```
3) Откройте http://localhost/ и документацию на http://localhost/redoc/

Остановка:
```
 docker-compose down -v
```

## Статика и демо-данные
- OpenAPI: `project_manager/static/redoc.yaml`
- CSV-данные: `project_manager/static/data/projects.csv`, `project_manager/static/data/tasks.csv`

## Лицензия
MIT
