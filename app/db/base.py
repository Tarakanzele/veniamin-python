from sqlalchemy.orm import DeclarativeBase


# DeclarativeBase — базовый класс для всех ORM-моделей проекта
# Все модели наследуются от Base, благодаря чему SQLAlchemy знает о них
# и Base.metadata содержит описание всех таблиц (используется Alembic)
class Base(DeclarativeBase):
    pass
