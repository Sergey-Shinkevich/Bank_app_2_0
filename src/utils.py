import datetime
import json
import pandas as pd
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Загружаем ключи из .env

def parse_date(date_str: str) -> datetime.datetime:
    """ Преобразует строку в объект datetime. Если формат неверный, возвращает текущую дату. """
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return pd.to_datetime(datetime.datetime.now())

def greeting(hour: int = None) -> str:
    """Возвращает приветствие в зависимости от часа."""
    if hour is None:
        hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро!"
    elif 12 <= hour < 18:
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


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют из внешнего API относительно RUB"""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    # Используем базовую валюту RUB, чтобы сразу видеть стоимость в рублях
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            rates = response.json().get("conversion_rates", {})
            # API дает: 1 RUB = X USD. Поэтому берем 1 / rates[currency]
            return [
                {"currency": c, "rate": round(1 / rates[c], 2)}
                for c in currencies if c in rates
            ]
    except Exception as e:
        print(f"Ошибка API валют: {e}")
    return []


def get_stock_prices(stocks: list) -> list:
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not stocks:
        return []
    symbols = ",".join(stocks)
    url = f"https://api.twelvedata.com/price?symbol={symbols}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        result = []
        # Проверяем, что пришел словарь
        if isinstance(data, dict):
            for stock in stocks:
                if stock in data:
                    price = data[stock].get("price")
                    if price:
                        result.append({"stock": stock, "price": round(float(price), 2)})
        return result

    except Exception as e:
        print(f"Ошибка при получении котировок: {e}")
        return []


