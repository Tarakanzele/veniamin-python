class StockWatchError(Exception):
    pass


class AssetNotFoundError(StockWatchError):
    pass


class UserNotFoundError(StockWatchError):
    pass


class UserAlreadyExistsError(StockWatchError):
    pass


class AlertNotFoundError(StockWatchError):
    pass


class AlertAlreadyExistsError(StockWatchError):
    pass


class NotificationError(StockWatchError):
    pass


class InvalidCredentialsError(StockWatchError):
    pass
