import datetime
import json
import pandas as pd
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Загружаем ключи из .env

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


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют из внешнего API относительно RUB"""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    # Используем базовую валюту RUB, чтобы сразу видеть стоимость в рублях
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            rates = response.json().get("conversion_rates", {})
            # API дает: 1 RUB = X USD. Нам нужно наоборот: 1 USD = X RUB.
            # Поэтому берем 1 / rates[currency]
            return [
                {"currency": c, "rate": round(1 / rates[c], 2)}
                for c in currencies if c in rates
            ]
    except Exception as e:
        print(f"Ошибка API валют: {e}")
    return []


#def get_stock_prices(stocks: list) -> list:
#    """Получает цены акций из внешнего API по тикерам"""
#    api_key = os.getenv("FINANCIAL_MODELING_API_KEY")
#    result = []

#    for stock in stocks:
#        url = f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={api_key}"
#        try:
#            response = requests.get(url, timeout=5)
#            if response.status_code == 200:
#                data = response.json()
#                if data:
#                    result.append({"stock": stock, "price": data[0].get("price")})
#        except Exception as e:
#            print(f"Ошибка API акций для {stock}: {e}")
#    return result


