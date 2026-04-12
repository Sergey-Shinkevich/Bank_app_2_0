import datetime
import json
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


def excel_read_to_pandas(path: str) -> pd.DataFrame:
    """Функция читает Excel-файл и возвращает Dataframe"""
    try:
        excel_data = pd.read_excel(path)
        return excel_data
    except Exception:
        return pd.DataFrame()

def list_of_field(df: pd.DataFrame, key: str) -> list:
    """Функция создает список уникальных значений поля таблицы"""
    if df.empty or key not in df.columns:
        return []
    return df[key].dropna().unique().tolist()

def get_user_settings(path: str) -> dict:
    """Читает пользовательские настройки из JSON-файла"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"user_currencies": ["USD", "EUR"], "user_stocks": []}


