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

def list_of_field(table: list, key: str) -> list:
    """Функция создает список уникальных значений поля таблицы"""
    result_set = set()
    for item in table:
        target = item.get(key)
        if target and str(target).lower() != 'nan':
            result_set.add(target)
    return list(result_set)



