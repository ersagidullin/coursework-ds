"""
Вспомогательный модуль.
Содержит процедуры, используемые другими модулями.
"""

import yaml

# получение токенов из secrets.yaml
def get_tokens(tokens):
    if len(tokens) == 0:
        return read_yaml("secrets.yaml", "tokens")

# ввод периода загрузки пользователем
def get_period(date_start="", date_end="", cancel = False):
    from datetime import datetime, time
    while date_start == "":
        date_str = input("Введите дату начала периода загрузки (dd.mm.yyyy) (0 - отмена загрузки)\n")
        #date_str = "01.01.2026"
        if date_str == "0":
            cancel = True
            return [date_start, date_end, cancel]
        try:
            date_start = datetime.strptime(date_str, "%d.%m.%Y").date()
            print("Дата начала периода " + date_start.strftime("%d.%m.%Y"))
            date_start = datetime.combine(date_start, time(0, 0, 0))
            break
        except ValueError:
            print("Ошибка! Неверный формат даты.")
    while date_end == "" or date_start > date_end:
        date_str = input("Введите дату окончания периода загрузки (dd.mm.yyyy) (0 - отмена загрузки)\n")
        #date_str = "01.02.2026"
        if date_str == "0":
            cancel = True
            return [date_start, date_end, cancel]
        try:
            date_end = datetime.strptime(date_str, "%d.%m.%Y").date()
            print("Дата окончания периода " + date_end.strftime("%d.%m.%Y"))
            date_end = datetime.combine(date_end, time(23, 59, 59))
            if date_start > date_end:
                print("Дата начала периода не может быть больше даты окончания периода.")
            else:
                return [date_start, date_end, cancel]
        except ValueError:
            print("Ошибка! Неверный формат даты.")

# получение значение поля .yaml (file_name - имя файла .yaml, key - наименование поля значение которого получаем)
def read_yaml(file_name, key):
    with open(file_name, "r") as file_object:
        secrets = yaml.load(file_object, Loader=yaml.SafeLoader)
        return secrets[key]

# (не используется) рекурсивное слияние настроек .yaml
def deep_merge(a, b):
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            deep_merge(a[key], b[key])
        else:
            a[key] = b[key]
    return a
