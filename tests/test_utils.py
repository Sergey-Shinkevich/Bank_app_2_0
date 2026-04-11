from unittest.mock import MagicMock, Mock, patch

import pytest

from src.utils import excel_read_to_dict, greeting, list_of_field


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


@patch("src.utils.pd.read_excel")
def test_excel_read_to_dict_normal(mock_read: Mock) -> None:
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
def test_excel_read_to_dict_abnormal(mock_read: Mock) -> None:
    """Тест на ошибку"""
    mock_read.side_effect = Exception
    result = excel_read_to_dict("../data/transactions_excel.xlsx")
    assert result == []
    mock_read.assert_called_once_with("../data/transactions_excel.xlsx")

def test_list_of_field_1(normal_data: list) -> None:
    """Тест функции на нормальные данные"""
    result = list_of_field(normal_data, "Статус")
    result.sort()
    assert result == ['FAILED', 'OK']

def test_list_of_field_2(abnormal_data: list) -> None:
    """Тест функции на не правильные данные"""
    result = list_of_field(abnormal_data, "Статус")
    assert result == []