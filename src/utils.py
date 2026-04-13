import datetime
import json
import os

import pandas as pd
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


def filter_operations_by_date(data: pd.DataFrame, date_obj: datetime.datetime) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца до указанной даты."""
    data["Дата операции"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
    start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
    # Фильтруем
    filtered_df = data[(data["Дата операции"] >= start_date) & (data["Дата операции"] <= date_obj)].copy()
    return filtered_df


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют из внешнего API относительно RUB"""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        print("Ошибка: Не задан API ключ валют")
        return []

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        rates = response.json().get("conversion_rates", {})
        result = []
        for c in currencies:
            # Проверяем, что валюта есть в списке и её курс не равен 0
            if c in rates and rates[c] != 0:
                result.append({"currency": c, "rate": round(1 / rates[c], 2)})
        return result

    except Exception as e:
        print(f"Ошибка API валют: {e}")
    return []

def calculate_cards_data(data: pd.DataFrame, cards_list: list, rates: list) -> list:
    """Считает общие траты и кешбэк по каждой карте с учетом конвертации валют."""
    # Превращаем список курсов в словарь для быстрого поиска: {"USD": 75.0, ...}
    rates_dict = {item["currency"]: item["rate"] for item in rates}
    result_cards = []

    for card_mask in cards_list:
        # Фильтруем операции по конкретной карте
        card_ops = data[data["Номер карты"] == card_mask]
        total_spent_rub = 0.0

        for _, op in card_ops.iterrows():
            amount = op["Сумма операции"]
            # Нас интересуют только траты (отрицательные значения)
            if amount < 0:
                currency = op["Валюта операции"]
                amount_abs = abs(float(amount))

                # Если валюта не рубли, конвертируем по курсу
                if currency != "RUB" and currency in rates_dict:
                    total_spent_rub += amount_abs * rates_dict[currency]
                else:
                    total_spent_rub += amount_abs

        result_cards.append({
            "last_digits": str(card_mask)[-4:],
            "total_spent": round(total_spent_rub, 2),
            "cashback": round(total_spent_rub / 100, 2)
        })

    return result_cards

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


