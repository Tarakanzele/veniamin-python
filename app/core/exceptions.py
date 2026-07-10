# Базовый класс для всех исключений проекта
# Позволяет поймать любую ошибку StockWatch одним except StockWatchError
class StockWatchError(Exception):
    pass


# Актив с таким тикером не найден в базе данных
class AssetNotFoundError(StockWatchError):
    pass


# Пользователь с таким id или email не найден
class UserNotFoundError(StockWatchError):
    pass


# Попытка зарегистрировать пользователя с уже существующим email
class UserAlreadyExistsError(StockWatchError):
    pass


# Алерт не найден или не принадлежит текущему пользователю
class AlertNotFoundError(StockWatchError):
    pass


# Попытка создать алерт, который уже существует
class AlertAlreadyExistsError(StockWatchError):
    pass


# Ошибка при отправке уведомления
class NotificationError(StockWatchError):
    pass


# Неверный email или пароль при попытке входа
class InvalidCredentialsError(StockWatchError):
    pass
