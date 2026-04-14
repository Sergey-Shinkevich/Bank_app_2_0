from src.services import get_top_cashback_categories
from src.utils import excel_read_to_dict, excel_read_to_pandas
from src.views import home_page
from src.reports import spending_by_category

def main() -> None:
    # Запуск Домашней Странички
    a = home_page("2020-04-13 23:15:00")
    print(a)

    # Запуск сервиса: "Выгодные категории повышенного кэшбэка"
    data = excel_read_to_dict("../data/operations.xlsx")
    b = get_top_cashback_categories(data, 2020, 4)
    print(b)

    # Запуск отчета трат по категориям
    data = excel_read_to_pandas("../data/operations.xlsx")
    c = spending_by_category(data, "Супермаркеты", "13-04-2020")
    print(c)

if __name__ == "__main__":
    main()
