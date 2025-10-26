import json
import os
from typing import List


class Entry:
    def __init__(self, title, entries=None, parent=None) -> None:
        if entries is None:
            entries = []
        self.title = title  # Наименование
        self.entries = entries  # записи
        self.parent = parent  # родительская запись

    # превращаем json в dict и создаем объект класса
    @classmethod
    def from_json(cls, value: dict):
        new_entry = Entry(value["title"])
        for sub_entry in value.get("entries", []):
            new_entry.add_entry(cls.from_json(sub_entry))
        return new_entry

    def __str__(self) -> str:
        return self.title

    def add_entry(self, entry):
        entry.parent = self
        self.entries.append(entry)

    # Печать с отступами
    def print_with_indent(self, indent: int = 0):
        tab = "    " * indent
        print(f"{tab}{self}")
        for entry in self.entries:
            entry.print_with_indent(indent + 1)

    # превращаем данные(dict) в json
    def json(self):
        res = {
            "title": self.title,
            "entries": [entry.json() for entry in self.entries]
        }
        return res

    # сохранения списка дел в json
    def save(self, path):
        dict1 = self.json()
        new_file = self.title + ".json"
        full_path = os.path.join(path, new_file)
        with open(full_path, "w", encoding='utf-8') as outfile:
            json.dump(dict1, outfile, indent=4, ensure_ascii=False)
            print(f'Файл по названием {new_file} создан')

    # берем данные из json и сохраняем новый объект класса
    @classmethod
    def load(cls, filename):
        with open(filename, "r", encoding='utf-8') as infile:
            return cls.from_json(json.load(infile))


class EntryManager:
    def __init__(self, data_path: str):
        self.data_path: str = data_path  # путь к данным
        self.entries: List[Entry] = []

    # сохранение записей
    def save(self):
        for entry in self.entries:
            entry.save(self.data_path)

    # Загружаем записи
    def load(self):
        for entry in os.listdir(self.data_path):
            if entry.endswith(".json"):
                new_enty = Entry.load(os.path.join(self.data_path, entry))
                self.entries.append(new_enty)

    # добавляет новую запись, принимая только её название
    def add_entry(self, title: str):
        self.entries.append(Entry(title))

# приложение готово
# нужно пройти по ссылке, там запущен Front
r'https://wexler.io/course/coding/todo-frontend/'

# залито на гит
