import json

import pytest

from src.services import get_top_cashback_categories


@pytest.fixture
def sample_data():
    """Фикстура для тестирования функции подсчета выгодных категорий кэшбэка"""
    return [
        {
            "Дата операции": "14.04.2026 10:00:00",
            "Категория": "Супермаркеты",
            "Сумма операции": -1000.0,
            "Валюта операции": "RUB",
        },
        {"Дата операции": "15.04.2026", "Категория": "Фастфуд", "Сумма операции": -350.0, "Валюта операции": "RUB"},
        {
            "Дата операции": "16.04.2026",
            "Категория": "Супермаркеты",
            "Сумма операции": -2000.0,
            "Валюта операции": "RUB",
        },
        {"Дата операции": "01.01.2026", "Категория": "Транспорт", "Сумма операции": -500.0, "Валюта операции": "RUB"},
        # Другой месяц и поплнение в плюс
        {"Дата операции": "17.04.2026", "Категория": "Связь", "Сумма операции": 500.0, "Валюта операции": "RUB"},
    ]


def test_get_top_cashback_categories_success(sample_data: list) -> None:
    """Проверка корректного расчета и сортировки."""
    result_json = get_top_cashback_categories(sample_data, 2026, 4)
    result = json.loads(result_json)
    assert result == {"Супермаркеты": 30, "Фастфуд": 3}
    assert list(result.keys())[0] == "Супермаркеты"


def test_get_top_cashback_categories_empty() -> None:
    """Проверка работы с пустым списком."""
    result_json = get_top_cashback_categories([], 2026, 4)
    assert json.loads(result_json) == {}


def test_get_top_cashback_categories_invalid_params(sample_data: list) -> None:
    """Проверка валидации некорректного месяца/года."""
    assert json.loads(get_top_cashback_categories(sample_data, 2026, 13)) == {}
    assert json.loads(get_top_cashback_categories(sample_data, "год", 4)) == {}


def test_get_top_cashback_categories_dirty_data() -> None:
    """Проверка устойчивости к 'битым' данным."""
    dirty_data: list = [
        {"Дата операции": "не дата", "Категория": "Х", "Сумма операции": -100.0},
        {"Дата операции": "20.04.2026", "Категория": "Y", "Сумма операции": "много"},
        None,
        {"Без даты": "совсем"},
    ]
    result_json = get_top_cashback_categories(dirty_data, 2026, 4)
    assert json.loads(result_json) == {}
