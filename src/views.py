from src.utils import greeting, list_of_field, excel_read_to_pandas


def home_page() -> dict:
    # Добавление приветствия
    result = {"greeting": greeting()}

    # Чтение файла с данными
    data = excel_read_to_pandas("../data/operations.xlsx")
    print(data)

    # Создание списка карт
    pd_card_number = list_of_field(data, 'Номер карты')
    print(pd_card_number)
    return result


a = home_page()
print(a)
