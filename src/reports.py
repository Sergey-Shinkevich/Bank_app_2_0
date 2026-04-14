from datetime import datetime
from typing import Optional

import pandas as pd

from src.logger import setup_logger

logger = setup_logger(__name__)


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Отчет по тратам за 3 месяца по категориям"""
    logger.info("Начало расчета трат по категориям за 3 месяца")
    # 1. Определяем конечную дату
    if date is None:
        end_date = pd.to_datetime(datetime.now())
    else:
        end_date = pd.to_datetime(date, dayfirst=True)

    # 2. Высчитываем начальную дату
    start_date = end_date - pd.Timedelta(days=90)

    # 3. Фильтруем данные
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_df = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] <= end_date)
        & (transactions["Дата операции"] >= start_date)
    ]
    logger.info("Окончание расчета трат по категориям за 3 месяца")
    return filtered_df
