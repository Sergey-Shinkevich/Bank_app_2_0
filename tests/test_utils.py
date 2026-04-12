from unittest.mock import Mock, patch
import pandas as pd
import pytest

from src.utils import excel_read_to_pandas, greeting, list_of_field


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


def test_excel_read_failure() -> None:
    """Тест, когда файл не найден или ошибка"""
    with patch('pandas.read_excel') as mock_read:
        mock_read.side_effect = Exception("System Error")
        result = excel_read_to_pandas("any_path.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert len(result) == 0

@pytest.mark.parametrize("column_name, expected", [("Номер карты", [4444, 5555]), ("Валюта", ["RUB", "USD"]), ("Несуществующая", [])])
def test_list_of_field(column_name, expected):
    """Тесты функции list_of_field"""
    df = pd.DataFrame({
        "Номер карты": [4444, 5555, 4444, None],
        "Валюта": ["RUB", "USD", "RUB", "RUB"]
    })
    result = list_of_field(df, column_name)
    assert result == expected