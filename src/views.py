from src.utils import greeting


def home_page() -> dict:
    # Добавление приветствия
    result = {"greeting": greeting()}
    return result


a = home_page()
print(a)
