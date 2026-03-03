import yaml
from datetime import datetime
# импорт глобальных переменных
from main import tokens

# получение токенов из secrets.yaml
def get_tokens(tokens):
    if len(tokens) == 0:
        return read_yaml("secrets.yaml", "tokens")


def get_period(date_start, date_end):
    if date_start == "" or date_end == "":
        date_str = input("Введите дату начала периода загрузки (dd.mm.yyyy)\n")
        try:
            global data_start
            data_start = datetime.strptime(date_str, "%d.%m.%Y").date()
            print(data_start)
        except ValueError:
            print("Ошибка! Неверный формат даты.")

# получение значение поля .yaml (file_name - имя файла .yaml, key - наименование поля значение которого получаем)
def read_yaml(file_name, key):
    with open(file_name, "r") as file_object:
        secrets = yaml.load(file_object, Loader=yaml.SafeLoader)
        return secrets[key]


# рекурсивное слияние настроек .yaml
def deep_merge(a, b):
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            deep_merge(a[key], b[key])
        else:
            a[key] = b[key]
    return a
