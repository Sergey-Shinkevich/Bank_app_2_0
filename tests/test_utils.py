from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    calculate_cards_data,
    excel_read_to_dict,
    excel_read_to_pandas,
    filter_operations_by_date,
    get_currency_rates,
    get_stock_prices,
    get_top_transactions,
    get_user_settings,
    greeting,
    list_of_field,
    parse_date,
)


def test_parse_date_normal() -> None:
    """Проверка корректной строки с датой"""
    date_str = "2020-04-13 23:15:00"
    result = parse_date(date_str)
    assert isinstance(result, pd.Timestamp) or isinstance(result, datetime)
    assert result.year == 2020
    assert result.month == 4
    assert result.day == 13


def test_parse_date_abnormal():
    """Проверка на неверный формат (должна вернуться текущая дата)"""
    date_str = "не дата"
    result = parse_date(date_str)
    now = datetime.now()
    # Проверяем, что год и месяц совпадают с текущими
    assert result.year == now.year
    assert result.month == now.month


@pytest.mark.parametrize(
    "hour, expected",
    [
        (2, "Доброй ночи!"),
        (8, "Доброе утро!"),
        (13, "Добрый день!"),
        (20, "Добрый вечер!"),
    ],
)
@patch("src.utils.datetime")
def test_greeting(mock_datetime: Mock, hour: int, expected: str) -> None:
    """Тест функции greeting"""
    mock_now = Mock()
    mock_now.hour = hour
    mock_datetime.datetime.now.return_value = mock_now
    result = greeting()
    assert result == expected
    mock_datetime.datetime.now.assert_called_once()


def test_excel_read_to_pandas_normal() -> None:
    """Тест успешного чтения файла"""
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = mock_df
        result = excel_read_to_pandas("any_path.xlsx")
        mock_read.assert_called_once_with("any_path.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]["col1"] == 1


def test_excel_read_to_pandas_failure() -> None:
    """Тест, когда файл не найден или ошибка"""
    with patch("pandas.read_excel") as mock_read:
        mock_read.side_effect = Exception("System Error")
        result = excel_read_to_pandas("any_path.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert len(result) == 0


@pytest.fixture
def sample_data():
    """Создаем тестовый DataFrame с транзакциями."""
    return pd.DataFrame(
        {
            "Дата операции": [
                "01.03.2020 10:00:00",  # Начало месяца (должно войти)
                "13.03.2020 15:00:00",  # Внутри диапазона (должно войти)
                "15.03.2020 10:00:00",  # После указанной даты (не должно войти)
                "28.02.2020 23:59:59",  # Прошлый месяц (не должно войти)
            ],
            "Сумма": [100, 200, 300, 400],
        }
    )


def test_filter_operations_by_date(sample_data):
    """тест функции filter_operations_by_date"""
    # Устанавливаем "сегодня" как 13 марта
    target_date = datetime(2020, 3, 13, 23, 59, 59)
    result = filter_operations_by_date(sample_data, target_date)
    # Должно остаться только 2 транзакции
    assert len(result) == 2
    # Проверяем, что даты в результате действительно те, что мы ждем
    dates = result["Дата операции"].dt.day.tolist()
    assert 1 in dates
    assert 13 in dates
    assert 15 not in dates
    assert 28 not in dates


@pytest.mark.parametrize(
    "column_name, expected", [("Номер карты", [4444, 5555]), ("Валюта", ["RUB", "USD"]), ("Несуществующая", [])]
)
def test_list_of_field(column_name: Any, expected: Any) -> None:
    """Тесты функции list_of_field"""
    df = pd.DataFrame({"Номер карты": [4444, 5555, 4444, None], "Валюта": ["RUB", "USD", "RUB", "RUB"]})
    result = list_of_field(df, column_name)
    assert result == expected


@pytest.fixture
def sample_rates():
    """Курсы валют для теста: 1 USD = 75 RUB, 1 EUR = 80 RUB"""
    return [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": 80.0}]


@pytest.fixture
def transactions_df():
    """Тестовые транзакции с разными валютами и картами."""
    return pd.DataFrame(
        {
            "Номер карты": ["*1111", "*1111", "*2222", "*1111"],
            "Сумма операции": [
                -100.0,  # Карта 1: Трата в рублях
                -10.0,  # Карта 1: Трата в USD (должна стать 750)
                -500.0,  # Карта 2: Трата в рублях
                200.0,  # Карта 1: Пополнение (должно игнорироваться)
            ],
            "Валюта операции": ["RUB", "USD", "RUB", "RUB"],
        }
    )


def test_calculate_cards_data_conversion(transactions_df, sample_rates):
    """Тест функции calculate_cards_data"""
    cards_list = ["*1111", "*2222"]
    result = calculate_cards_data(transactions_df, cards_list, sample_rates)

    # Проверка для карты *1111: 100 (RUB) + 10 * 75 (USD) = 100 + 750 = 850
    card1 = next(c for c in result if c["last_digits"] == "1111")
    assert card1["total_spent"] == 850.0
    assert card1["cashback"] == 8.5
    # Проверка для карты *2222: Только одна трата 500
    card2 = next(c for c in result if c["last_digits"] == "2222")
    assert card2["total_spent"] == 500.0
    assert card2["cashback"] == 5.0


def test_calculate_cards_data_empty_or_no_match(sample_rates):
    """Тест на пустой DF"""
    df_empty = pd.DataFrame(columns=["Номер карты", "Сумма операции", "Валюта операции"])
    result = calculate_cards_data(df_empty, ["*1111"], sample_rates)
    assert len(result) == 1
    assert result[0]["total_spent"] == 0


def test_get_user_settings_success() -> None:
    """Тест успешного чтения настроек JSON"""
    mock_config = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}'
    with patch("builtins.open", mock_open(read_data=mock_config)):
        result = get_user_settings("fake_path.json")
    assert result == {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}
    assert "user_currencies" in result


def test_get_user_settings_file_not_found() -> None:
    """Тест, когда файла конфигурации нет"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_user_settings("missing_path.json")
    assert isinstance(result, dict)
    assert result.get("user_currencies") == ["USD", "EUR"]


def test_get_user_settings_invalid_json() -> None:
    """Синтаксическая ошибка в файле"""
    mock_bad_config = '{"user_currencies": ["USD", "EUR"'  # Нет закрывающей скобки
    with patch("builtins.open", mock_open(read_data=mock_bad_config)):
        result = get_user_settings("bad_path.json")
    assert result == {"user_currencies": ["USD", "EUR"], "user_stocks": []}


@patch("requests.get")
def test_get_currency_rates_success(mock_get: Mock) -> None:
    """Тестируем успешный ответ от API"""
    # Имитируем структуру ответа от ExchangeRate-API
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"conversion_rates": {"USD": 0.011, "EUR": 0.010}}
    # Вызываем функцию
    result = get_currency_rates(["USD", "EUR"])
    # Проверяем расчет (1 / 0.011 ≈ 90.91)
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] > 0
    assert isinstance(result[0]["rate"], float)


@patch("requests.get")
def test_get_currency_rates_server_error(mock_get: Mock) -> None:
    """Тестируем поведение при ошибке сервера (500)"""
    mock_get.return_value.status_code = 500
    result = get_currency_rates(["USD"])
    assert result == []


@patch("requests.get")
def test_get_currency_rates_exception(mock_get: Mock) -> None:
    """Тестируем отсутствие связи"""
    mock_get.side_effect = Exception("No internet")
    result = get_currency_rates(["USD"])
    assert result == []


def test_get_top_transactions_sorting():
    """Проверяем, что в ТОП-5 попадают самые крупные операции по модулю."""
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["2021-12-01", "2021-12-02", "2021-12-03", "2021-12-04", "2021-12-05", "2021-12-06"]
            ),
            "Сумма операции": [
                -15000.0,  # 1-е место (самый большой расход)
                10000.0,  # 2-е место (самый большой доход)
                -500.0,  # 5-е место
                2000.0,  # 3-е место
                -1000.0,  # 4-е место
                10.0,  # Должно не попасть в ТОП
            ],
            "Категория": ["ЖКХ", "Зарплата", "Еда", "Переводы", "Такси", "Мелочь"],
            "Описание": ["Квартира", "Работа", "Бургер", "Другу", "Uber", "Жвачка"],
        }
    )
    result = get_top_transactions(df)
    # Проверяем количество
    assert len(result) == 5
    assert result[0]["amount"] == -15000.0
    assert result[0]["category"] == "ЖКХ"
    assert result[1]["amount"] == 10000.0
    # Проверяем, что самая мелкая операция (10.0) не попала в список
    amounts = [item["amount"] for item in result]
    assert 10.0 not in amounts


def test_get_top_transactions_empty():
    """Проверка работы с пустым DataFrame."""
    df_empty = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория", "Описание"])
    assert get_top_transactions(df_empty) == []


@patch("requests.get")
def test_get_stock_prices_batch(mock_get: Mock) -> None:
    """Тестируем, что функция корректно обрабатывает склеенный ответ"""
    # Имитируем ответ API Twelve Data)
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"AAPL": {"price": "150.00"}, "MSFT": {"price": "300.00"}}
    # Вызываем нашу функцию
    stocks = ["AAPL", "MSFT"]
    result = get_stock_prices(stocks)
    # Проверяем, что вернулось именно 2 акции
    assert len(result) == 2
    # Проверяем точность данных
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.00
    # Проверяем, что запрос ушел один
    assert mock_get.call_count == 1


@patch("requests.get")
def test_get_stock_prices_network_error(mock_get: Mock) -> None:
    """Тестируем поведение при падении сети"""
    mock_get.side_effect = Exception("Connection error")

    result = get_stock_prices(["AAPL"])

    # Проверяем, что программа не «упала», а вернула пустой список
    assert result == []


@patch("src.utils.pd.read_excel")
def test_excel_read_to_dict_normal(mock_read):
    """Тест на нормальные данные"""
    mock_df = MagicMock()
    fake = [
        {
            "id": "650703",
            "state": "EXECUTED",
            "date": "2023-09-05T11:30:32Z",
            "amount": "16210",
            "currency_name": "Sol",
            "currency_code": "PEN",
            "from": "Счет 58803664561298323391",
            "to": "Счет 39745660563456619397",
            "description": "Перевод организации",
        },
        {
            "id": "3598919",
            "state": "EXECUTED",
            "date": "2020-12-06T23:00:58Z",
            "amount": "29740",
            "currency_name": "Peso",
            "currency_code": "COP",
            "from": "Discover 3172601889670065",
            "to": "Discover 0720428384694643",
            "description": "Перевод с карты на карту",
        },
        {
            "id": "593027",
            "state": "CANCELED",
            "date": "2023-07-22T05:02:01Z",
            "amount": "30368",
            "currency_name": "Shilling",
            "currency_code": "TZS",
            "from": "Visa 1959232722494097",
            "to": "Visa 6804119550473710",
            "description": "Перевод с карты на карту",
        },
    ]
    mock_df.to_dict.return_value = fake
    mock_read.return_value = mock_df
    result = excel_read_to_dict("../data/transactions_excel.xlsx")
    assert result == fake
    mock_read.assert_called_once_with("../data/transactions_excel.xlsx")


@patch("src.utils.pd.read_excel")
def test_excel_read_to_dict_abnormal(mock_read):
    """Тест на ошибку"""
    mock_read.side_effect = Exception
    result = excel_read_to_dict("../data/operations.xlsx")
    assert result == []
    mock_read.assert_called_once_with("../data/operations.xlsx")
