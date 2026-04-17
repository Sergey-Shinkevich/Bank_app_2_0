import pandas as pd
import pytest
from freezegun import freeze_time

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions():
    """Фикстура для тестирования трат за три месяца по категории"""
    data = {
        "Дата операции": [
            "14.04.2026",  # Сегодня
            "14.03.2026",  # 1 месяц назад
            "14.02.2026",  # 2 месяца назад
            "14.01.2026",  # 3 месяца назад (граница)
            "14.12.2025",  # (не должно войти)
            "15.04.2026",  # Будущее (не должно войти)
        ],
        "Категория": ["Фастфуд", "Фастфуд", "Супермаркеты", "Фастфуд", "Фастфуд", "Фастфуд"],
        "Сумма операции": [-100, -200, -500, -300, -400, -100],
    }
    return pd.DataFrame(data)


def test_spending_by_category_filter(sample_transactions: pd.DataFrame) -> None:
    """Проверка фильтрации по категории и дате."""
    # Тестируем категорию Фастфуд от 14.04.2026
    result = spending_by_category(sample_transactions, "Фастфуд", "14.04.2026")
    assert len(result) == 3
    assert all(result["Категория"] == "Фастфуд")
    assert result["Сумма операции"].sum() == -600


@freeze_time("2026-04-14")
def test_spending_by_category_none_date(sample_transactions):
    """Тест работает имитируя 14 апреля 2026 года."""
    result = spending_by_category(sample_transactions, "Фастфуд")
    assert len(result) == 3


def test_spending_by_category_empty_res(sample_transactions):
    """Проверка случая, когда категория не найдена."""
    result = spending_by_category(sample_transactions, "Аптеки", "14.04.2026")
    assert result.empty


def test_spending_by_category_out_of_range(sample_transactions):
    """Проверка, что очень старые транзакции не попадают."""
    result = spending_by_category(sample_transactions, "Фастфуд", "14.04.2028")
    assert len(result) == 0
