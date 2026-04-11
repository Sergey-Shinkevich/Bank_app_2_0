import datetime


def greeting(hour: int | None = None) -> str:
    """Возвращает приветствие на основе переданного или текущего часа"""
    if hour is None:
        hour = datetime.datetime.now().hour

    if 5 <= hour < 11:
        return "Доброе утро!"
    elif 11 <= hour < 18:
        return "Добрый день!"
    elif 18 <= hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


print(greeting(23))
