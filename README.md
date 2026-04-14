# Курсовая работа №1
____
Тема: Разработка приложения для анализа транзакций, которые находятся в Excel-файле. 
Приложение генерирует:
____
 - JSON - данные для веб-страницы "Главная". 
 - JSON - данные для страницы "Сервис: Выгодные категории повышенного кешбэка".
 - JSON - данные для страницы "Отчет: Траты по категории".
____
## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/Sergey-Shinkevich/Bank_app_2_0] (https://github.com/Sergey-Shinkevich/Bank_app_2_0)
2. Установите зависимости через Poetry:
   ```bash
   poetry install
3. Для запуска тестов и генерации отчета о покрытии:
   ```bash
   pytest --cov=src

____
## Использованные API сервисы
- Для получения курсов валют: Exchange Rate-API https://www.exchangerate-api.com/
- Для получения котировок акций из списка S&P500: Twelve Data https://twelvedata.com/ 
____
## Зависимости основные
- Python 3.14.2
- Openpyxl 3.1.5
- Pandas 3.0.2
- Python-Dotenv 1.2.2
- Requests 2.33.1
____
## Зависимости для разработки
- Black 26.3.1
- Flake8 7.3.0
- Freezegun 1.5.5
- Isort 8.0.1
- Mypy 1.20.0
- Pandas-Stubs 3.0.0.260204
- Pytest 9.0.3 
- Pytest-Cov 7.1.0
____
## Покрытие тестами
```
Name                     Stmts   Miss  Cover
--------------------------------------------
src\__init__.py              0      0   100%
src\logger.py               16      1    94%
src\reports.py              15      0   100%
src\services.py             37      0   100%
src\utils.py               146      6    96%
tests\__init__.py            0      0   100%
tests\test_reports.py       23      0   100%
tests\test_services.py      21      0   100%
tests\test_utils.py        158      0   100%
--------------------------------------------
TOTAL                      416      7    98%

