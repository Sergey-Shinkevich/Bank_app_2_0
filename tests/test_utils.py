from typing import Any
from unittest.mock import Mock, patch, mock_open
import pandas as pd
import pytest
from src.utils import excel_read_to_pandas, greeting, list_of_field, get_user_settings, get_currency_rates, get_stock_prices


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
        assert result.iloc[0]['col1'] == 1


def test_excel_read_to_pandas_failure() -> None:
    """Тест, когда файл не найден или ошибка"""
    with patch('pandas.read_excel') as mock_read:
        mock_read.side_effect = Exception("System Error")
        result = excel_read_to_pandas("any_path.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert len(result) == 0

@pytest.mark.parametrize("column_name, expected", [("Номер карты", [4444, 5555]), ("Валюта", ["RUB", "USD"]), ("Несуществующая", [])])
def test_list_of_field(column_name: Any, expected: Any) -> None:
    """Тесты функции list_of_field"""
    df = pd.DataFrame({
        "Номер карты": [4444, 5555, 4444, None],
        "Валюта": ["RUB", "USD", "RUB", "RUB"]
    })
    result = list_of_field(df, column_name)
    assert result == expected


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
    assert result.get("user_currencies") == ['USD', 'EUR']


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
    mock_get.return_value.json.return_value = {"conversion_rates":{"USD": 0.011, "EUR": 0.010}}
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
    """Тестируем отсутствии связи"""
    mock_get.side_effect = Exception("No internet")
    result = get_currency_rates(["USD"])
    assert result == []

@patch("requests.get")
def test_get_stock_prices_batch(mock_get: Mock) -> None:
    """Тестируем, что функция корректно обрабатывает склеенный ответ"""
    # Имитируем ответ API Twelve Data)
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "AAPL": {"price": "150.00"},
        "MSFT": {"price": "300.00"}
    }
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