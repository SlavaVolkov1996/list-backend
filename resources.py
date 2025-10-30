import json
import os
import shutil
from typing import List


class Entry:
    def __init__(self, title, entries=None, parent=None, entry_id=None):
        if entries is None:
            entries = []
        self.id = entry_id or self.generate_id()  # Уникальный ID для идентификации
        self.title = title
        self.entries = entries
        self.parent = parent

    def generate_id(self):
        import uuid
        return str(uuid.uuid4())

    # превращаем json в dict и создаем объект класса
    @classmethod
    def from_json(cls, value: dict):
        # Используем существующий ID или создаем новый
        entry_id = value.get("id")
        new_entry = Entry(value["title"], entry_id=entry_id)

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
        return {
            "id": self.id,  # Включаем ID в JSON
            "title": self.title,
            "entries": [entry.json() for entry in self.entries]
        }

    # сохранения списка дел в json
    def save(self, path):
        # Используем ID как имя файла для однозначной идентификации
        filename = f"{self.id}.json"
        full_path = os.path.join(path, filename)

        # Создаем директорию если не существует
        os.makedirs(path, exist_ok=True)

        with open(full_path, "w", encoding='utf-8') as outfile:
            json.dump(self.json(), outfile, indent=4, ensure_ascii=False)
            print(f'Файл с ID {self.id} создан/обновлен')

    # берем данные из json и сохраняем новый объект класса
    @classmethod
    def load(cls, filename):
        with open(filename, "r", encoding='utf-8') as infile:
            content = infile.read()
            if not content.strip():  # Проверяем что файл не пустой
                return None
            return cls.from_json(json.loads(content))


class EntryManager:
    def __init__(self, data_path: str):
        self.data_path: str = data_path  # путь к данным
        self.entries: List[Entry] = []

    # сохранение записей с удалением старых файлов
    def save(self):
        os.makedirs(self.data_path, exist_ok=True)

        # Получаем ID всех текущих записей (включая вложенные)
        current_ids = self._get_all_entry_ids(self.entries)

        # Получаем ID всех существующих файлов
        existing_files = self._get_existing_json_files()

        # Удаляем файлы, которых нет в текущих записях
        self._cleanup_orphaned_files(current_ids, existing_files)

        # Сохраняем все текущие записи
        for entry in self.entries:
            self._save_entry_recursive(entry)

    # Рекурсивное сохранение записи и всех подзаписей
    def _save_entry_recursive(self, entry):
        entry.save(self.data_path)
        for sub_entry in entry.entries:
            self._save_entry_recursive(sub_entry)

    # Получение всех ID записей (рекурсивно)
    def _get_all_entry_ids(self, entries):
        entry_ids = set()
        for entry in entries:
            entry_ids.add(entry.id)
            # Рекурсивно получаем ID подзаписей
            entry_ids.update(self._get_all_entry_ids(entry.entries))
        return entry_ids

    # Получение списка существующих JSON файлов
    def _get_existing_json_files(self):
        if not os.path.exists(self.data_path):
            return set()

        json_files = set()
        for filename in os.listdir(self.data_path):
            if filename.endswith(".json"):
                # Извлекаем ID из имени файла (убираем .json)
                file_id = filename[:-5]
                json_files.add(file_id)
        return json_files

    # Удаление файлов, которых нет в текущих записях
    def _cleanup_orphaned_files(self, current_ids, existing_files):
        files_to_delete = existing_files - current_ids

        for file_id in files_to_delete:
            file_path = os.path.join(self.data_path, f"{file_id}.json")
            try:
                os.remove(file_path)
                print(f"Удален orphaned файл: {file_id}.json")
            except OSError as e:
                print(f"Ошибка при удалении файла {file_id}.json: {e}")

    # Загружаем записи
    def load(self):
        self.entries.clear()  # Очищаем текущие записи

        if not os.path.exists(self.data_path):
            return

        loaded_entries = []
        loaded_ids = set()

        # Загружаем все JSON файлы
        for filename in os.listdir(self.data_path):
            if filename.endswith(".json"):
                full_path = os.path.join(self.data_path, filename)
                try:
                    entry = Entry.load(full_path)
                    if entry and entry.id not in loaded_ids:
                        loaded_entries.append(entry)
                        loaded_ids.add(entry.id)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Ошибка загрузки файла {filename}: {e}")
                    continue

        # Строим иерархию записей
        self.entries = self._build_hierarchy(loaded_entries)

    # Вспомогательный метод для построения иерархии (если нужно)
    def _build_hierarchy(self, entries):
        # В текущей реализации каждая запись независима
        # Если в будущем понадобится строить иерархию, можно доработать
        return entries

    # добавляет новую запись, принимая только её название
    def add_entry(self, title: str):
        new_entry = Entry(title)
        self.entries.append(new_entry)
        return new_entry

    # Удаление записи по ID (рекурсивно)
    def delete_entry(self, entry_id: str):
        self.entries = self._delete_entry_recursive(self.entries, entry_id)
        return self.entries

    def _delete_entry_recursive(self, entries, entry_id):
        updated_entries = []
        for entry in entries:
            if entry.id == entry_id:
                # Нашли запись для удаления - пропускаем её
                print(f"Запись {entry_id} помечена для удаления")
                continue
            else:
                # Рекурсивно проверяем подзаписи
                entry.entries = self._delete_entry_recursive(entry.entries, entry_id)
                updated_entries.append(entry)
        return updated_entries