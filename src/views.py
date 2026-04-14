import json
from typing import Any

from mypy.exportjson import Json

from src.utils import (excel_read_to_pandas, get_currency_rates, get_stock_prices, get_user_settings, greeting,
                       list_of_field, parse_date, filter_operations_by_date, calculate_cards_data, get_top_transactions)

def home_page(date_str: str) -> Json:
    """Домашняя страница"""
    # 1. Проверка, что введена аргумент функции именно формат даты.
    date_obj = parse_date(date_str)

    # 2. Добавление приветствия
    result: dict[str, Any] = {"greeting": greeting(date_obj.hour)}

    # 3. Чтение данных из файлов
    data = excel_read_to_pandas("../data/operations.xlsx")
    settings = get_user_settings("../user_settings.json")

    # 4. Фильтрация банковских операций по заданному временному промежутку
    data_filtered = filter_operations_by_date(data, date_obj)

    # 5. Создание списка всех валют из файла данных
    excel_currencies_all = list_of_field(data_filtered,"Валюта операции")

    # 6. Создание списка иностранных валют из списка всех валют
    excel_currencies_foreign = [x for x in excel_currencies_all if x != 'RUB']

    # 7. Подготовка списка валют для API-запроса.
    user_currencies = settings.get("user_currencies", [])
    all_needed_currencies = list(set(user_currencies + excel_currencies_foreign))

    # 8. Один запрос к API за всеми курсами сразу
    currencies_data: list[dict] = get_currency_rates(all_needed_currencies)

    # 9. Создание списка карт
    pd_card_number = list_of_field(data_filtered, 'Номер карты')

    # 10. Расчет данных по картам
    result["cards"] = calculate_cards_data(data_filtered, pd_card_number, currencies_data)

    # 11. Получаем ТОП-5 самых крупных трат
    result["top_transactions"] = get_top_transactions(data_filtered)

    # 12. Добавили необходимы курсы валют
    result["currency_rates"] = [item for item in currencies_data if isinstance(item, dict) and item.get("currency") in user_currencies]

    # 13. Добавили курсы необходимых акций
    user_stocks = settings.get("user_stocks", [])
    result["stock_prices"] = get_stock_prices(user_stocks)

    return json.dumps(result, ensure_ascii=False, indent=4)






