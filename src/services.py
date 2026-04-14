import json
from datetime import datetime

from src.logger import setup_logger

logger = setup_logger(__name__)


def get_top_cashback_categories(data: list[dict], year: int, month: int):
    """Рассчитывает кэшбэк по категориям."""
    logger.info("Начало расчета категорий повышенного кэшбэка")
    cashback_result = {}
    # 1. Валидация входных параметров
    if not isinstance(data, list) or not data:
        logger.warning("Не корректный тип данных data")
        return json.dumps({}, ensure_ascii=False)
    if not (isinstance(year, int) and isinstance(month, int) and 1 <= month <= 12):
        logger.warning("Не корректный тип данных даты")
        return json.dumps({}, ensure_ascii=False)
    for operation in data:
        if not isinstance(operation, dict):
            continue
        date_str = operation.get("Дата операции")
        if not date_str:
            continue
        # 2. Проверяем формат даты и правим если не DD.MM.YYYY или пропускаем операции по исключению
        try:
            clean_date = str(date_str)[:10]
            op_date = datetime.strptime(clean_date, "%d.%m.%Y")
        except (ValueError, TypeError):
            logger.error(f"Не корректный тип данных даты {date_str}")
            continue
        # 3. Фильтрация по периоду
        if op_date.year == year and op_date.month == month:
            category = operation.get("Категория", "Разное")
            amount = operation.get("Сумма операции", 0)
            if isinstance(amount, (int, float)) and amount < 0:
                cashback = int(abs(amount) / 100)
                if cashback > 0:
                    if category not in cashback_result:
                        cashback_result[category] = 0
                    cashback_result[category] += cashback

    # Сортируем словарь
    sorted_cashback = dict(sorted(cashback_result.items(), key=lambda item: item[1], reverse=True))
    logger.info("Окончание расчета категорий повышенного кэшбэка")
    return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)
