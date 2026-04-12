from typing import Any

from src.utils import greeting, list_of_field, excel_read_to_pandas, get_user_settings, get_currency_rates, \
    get_stock_prices, parse_date


def home_page(date_str: str) -> dict:

    # 1. Проверка, что введена аргумент функции именно формат даты.
    date_obj = parse_date(date_str)

    # 2. Добавление приветствия
    result: dict[str, Any] = {"greeting": greeting(date_obj.hour)}

    # Чтение данных из файлов
    data = excel_read_to_pandas("../data/operations.xlsx")
    settings = get_user_settings("../user_settings.json")

    # Создание списка всех валют из файла данных
    excel_currencies_all = list_of_field(data,"Валюта операции")

    # Создание списка иностранных валют из списка всех валют
    excel_currencies_foreign = [x for x in excel_currencies_all if x != 'RUB']

    # Подготовка списка валют для API-запроса.
    user_currencies = settings.get("user_currencies", [])
    all_needed_currencies = list(set(user_currencies + excel_currencies_foreign))

    # Один запрос к API за всеми курсами сразу
    # currencies_data: list[dict] = get_currency_rates(all_needed_currencies)
    # result["currency_rates"] = [item for item in currencies_data if isinstance(item, dict) and item.get("currency") in user_currencies]

    # Один запрос к биржевым тикетам
    # user_stocks = settings.get("user_stocks", [])
    # result["stock_prices"] = get_stock_prices(user_stocks)

    # Создание списка карт
    # pd_card_number = list_of_field(data, 'Номер карты')
    return result


a = home_page("2020-04-13 23:15:00")
print(a)
