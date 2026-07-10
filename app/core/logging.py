import logging
import sys


def setup_logging() -> None:
    # basicConfig настраивает корневой логгер один раз при старте приложения
    logging.basicConfig(
        # INFO — показывает обычные события; WARNING и ERROR — проблемы
        level=logging.INFO,
        # Формат: время | уровень | имя логгера | сообщение
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        # Вывод идёт в stdout, чтобы Docker и системы логирования могли его собирать
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# Именованный логгер проекта — все модули используют его через импорт
logger = logging.getLogger("stockwatch")
