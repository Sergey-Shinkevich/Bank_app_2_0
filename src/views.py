from src.utils import greeting, list_of_field, excel_read_to_pandas, get_user_settings


def home_page() -> dict:
    # Добавление приветствия
    result = {"greeting": greeting()}

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

    # 4. Один запрос к API за всеми курсами сразу
    # currencies_data = get_currency_rates(all_needed_currencies)

    # Создание списка карт
    pd_card_number = list_of_field(data, 'Номер карты')
    return result


a = home_page()
print(a)
