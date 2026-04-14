import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from src.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()  # Загружаем ключи из .env

def parse_date(date_str: str) -> datetime.datetime:
    """ Преобразует строку в объект datetime. Если формат неверный, возвращает текущую дату. """
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        logger.error(f"Не верный формат даты {date_str}")
        return pd.to_datetime(datetime.datetime.now())

def greeting(hour: int = None) -> str:
    """Возвращает приветствие в зависимости от часа."""
    if hour is None:
        hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        logger.info("Приветствие: Доброе утро!")
        return "Доброе утро!"
    elif 12 <= hour < 18:
        logger.info("Приветствие: Добрый день!")
        return "Добрый день!"
    elif 18 <= hour < 23:
        logger.info("Приветствие: Добрый вечер!")
        return "Добрый вечер!"
    else:
        logger.info("Приветствие: Доброй ночи!")
        return "Доброй ночи!"

def excel_read_to_pandas(path: str) -> pd.DataFrame:
    """Функция читает Excel-файл и возвращает Dataframe"""
    logger.info("Чтение Excel файла с преобразованием в Pandas началось")
    try:
        excel_data = pd.read_excel(path)
        logger.info("Чтение Excel файла с преобразованием в Pandas успешно завершено")
        return excel_data
    except Exception:
        logger.error(f"Ошибка {Exception} при чтении Excel файла с преобразованием в Pandas")
        return pd.DataFrame()

def list_of_field(df: pd.DataFrame, key: str) -> list:
    """Функция создает список уникальных значений поля таблицы"""
    if df.empty or key not in df.columns:
        logger.warning(f"Создание уникальных значений поля {key} прошло неудачно")
        return []
    logger.info(f"Создание уникальных значений поля {key} завершено")
    return df[key].dropna().unique().tolist()

def get_user_settings(path: str) -> dict:
    """Читает пользовательские настройки из JSON-файла"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            logger.info("Чтение пользовательских настроек прошло удачно")
            return json.load(f)
    except Exception:
        logger.error(f"Чтение пользовательских настроек привело к ошибке: {Exception}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": []}


def filter_operations_by_date(data: pd.DataFrame, date_obj: datetime.datetime) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца до указанной даты."""
    data["Дата операции"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
    start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
    # Фильтруем
    filtered_df = data[(data["Дата операции"] >= start_date) & (data["Дата операции"] <= date_obj)].copy()
    logger.info(f"Фильтрация транзакций с начала месяца до указанной даты прошла успешно")
    return filtered_df


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют из внешнего API относительно RUB"""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        print("Ошибка: Не задан API ключ валют")
        logger.error("Ошибка: Не задан API ключ валют")
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
        logger.info("Курсы валют скачены успешно")
        return result

    except Exception as e:
        logger.error(f"Ошибка API валют {Exception}")
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
    logger.info("Подсчет операций по картам завершен")
    return result_cards


def get_top_transactions(data: pd.DataFrame) -> list[dict]:
    """Возвращает 5 самых крупных по сумме операций (любых)."""
    if data.empty:
        logger.error("Нет данных для подсчета 5 самых крупных операций")
        return []

    df_copy = data.copy()

    # Сортируем по абсолютному значению суммы (модулю) от большего к меньшему
    df_copy["abs_amount"] = df_copy["Сумма операции"].abs()
    top_5_df = df_copy.sort_values(by="abs_amount", ascending=False).head(5)

    top_transactions = []
    for _, row in top_5_df.iterrows():
        top_transactions.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(float(row["Сумма операции"]), 2),
            "category": str(row["Категория"]),
            "description": str(row["Описание"])
        })
    logger.info("Подсчет 5 самых крупных операций завершен")
    return top_transactions


def get_stock_prices(stocks: list) -> list:
    """Получение котировок акций"""
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not stocks:
        logger.error("Нет данных по акциям")
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
        logger.info("Данные по акциям получены успешно")
        return result

    except Exception as e:
        print(f"Ошибка при получении котировок: {e}")
        logger.error(f"Ошибка при получении котировок: {e}")
        return []


def excel_read_to_dict(path: str) -> list:
    """ Читает Excel-файл и возвращает данные в виде списка словарей. """
    try:
        df = pd.read_excel(path)
        data = df.to_dict(orient='records')
        # Заменяем NaN на None
        for row in data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
        logger.info("Чтение Excel файла в список словарей прошел удачно")
        return data
    except Exception as e:
        logger.info(f"Чтение Excel файла в список словарей прошел с ошибкой {e}")
        print(f"Ошибка при чтении файла: {e}")
        return []
