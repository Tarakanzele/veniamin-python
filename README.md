# StockWatch

Сервис мониторинга финансовых активов. Backend уровня production на Python 3.11+.

## Стек

| Компонент | Технология |
|-----------|-----------|
| API | FastAPI |
| База данных | PostgreSQL + SQLAlchemy 2.0 |
| Миграции | Alembic |
| Кеш / Брокер | Redis |
| Фоновые задачи | Celery + Celery Beat |
| Аутентификация | JWT (python-jose + bcrypt) |
| Real-time | WebSocket |
| Тесты | pytest + pytest-asyncio + httpx |

## Быстрый старт

```bash
cp .env.example .env
# Отредактируй .env: установи SECRET_KEY и пароли

docker compose up --build
```

После запуска доступно:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API

### Аутентификация

```
POST /api/v1/auth/register   — регистрация
POST /api/v1/auth/login      — получение JWT токена
GET  /api/v1/auth/me         — текущий пользователь
```

### Активы

```
GET    /api/v1/assets/                   — список активов
POST   /api/v1/assets/                   — добавить актив
GET    /api/v1/assets/{ticker}           — актив по тикеру
PATCH  /api/v1/assets/{ticker}           — обновить актив
DELETE /api/v1/assets/{ticker}           — удалить актив
GET    /api/v1/assets/{ticker}/price     — текущая цена (из кеша)
GET    /api/v1/assets/{ticker}/prices    — история цен
POST   /api/v1/assets/{ticker}/prices    — добавить цену вручную
```

### Уведомления

```
GET    /api/v1/alerts/                   — список алертов
POST   /api/v1/alerts/                   — создать алерт
PATCH  /api/v1/alerts/{id}               — включить/выключить
DELETE /api/v1/alerts/{id}               — удалить алерт
GET    /api/v1/alerts/notifications      — история уведомлений
```

### Аналитика

```
GET /api/v1/analytics/{ticker}?limit=100 — min/max/avg/change
```

### WebSocket

```
WS /api/v1/ws/prices/{ticker} — real-time поток цен
```

## Алерты

Условия: `above` (цена выше значения) и `below` (цена ниже значения).

Celery Beat проверяет алерты каждые 5 минут. При срабатывании алерт отключается и создаётся запись в `NotificationHistory`.

## Миграции

```bash
# Применить миграции
docker compose exec api alembic upgrade head

# Создать новую миграцию
docker compose exec api alembic revision --autogenerate -m "описание"
```

## Тесты

```bash
pip install -r requirements.txt
pytest --cov=app tests/
```

## Архитектура

```
API (роуты)
 ↓
Service (бизнес-логика)
 ↓
Repository (работа с БД)
 ↓
Database (PostgreSQL)
```

Рыночные данные абстрагированы через `MarketProvider` Protocol — провайдер можно заменить без изменения бизнес-логики.
