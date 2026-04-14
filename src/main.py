from src.services import get_top_cashback_categories
from src.utils import excel_read_to_dict
from src.views import home_page


def main() -> None:
    # Запуск Домашней Странички
    # a = home_page("2020-04-13 23:15:00")
    # print(a)

    # Подготовка данных для сервиса: "Выгодные категории повышенного кэшбэка"
    data = excel_read_to_dict("../data/operations.xlsx")
    b = get_top_cashback_categories(data, 2020, 4)
    print(b)


if __name__ == "__main__":
    main()
