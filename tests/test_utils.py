from unittest.mock import Mock, patch

import pytest

from src.utils import greeting


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
