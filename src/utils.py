import datetime

import pandas as pd


def greeting(hour: int | None = None) -> str:
    """Возвращает приветствие на основе переданного или текущего часа"""
    if hour is None:
        hour = datetime.datetime.now().hour

    if 5 <= hour < 11:
        return "Доброе утро!"
    elif 11 <= hour < 18:
        return "Добрый день!"
    elif 18 <= hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def excel_read_to_dict(path: str) -> list:
    """Функция читает Excel-файл и возвращает список словарей"""
    try:
        excel_data = pd.read_excel(path)
        result = excel_data.to_dict(orient="records")
        return result
    except Exception:
        return []
