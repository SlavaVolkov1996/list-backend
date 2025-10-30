from flask import Flask, request, jsonify
from resources import EntryManager, Entry
import os

FOLDER = os.environ.get('FOLDER', '/app/data')
app = Flask(__name__)


@app.route("/api/entries/")
def get_entries():
    entry_manager = EntryManager(FOLDER)
    entry_manager.load()
    return jsonify([entry.json() for entry in entry_manager.entries])


@app.route("/api/save_entries/", methods=["POST"])
def save_entries():
    entry_manager = EntryManager(FOLDER)
    entries_data = request.get_json()

    # Загружаем текущие записи чтобы понимать что удалять
    entry_manager.load()

    # Очищаем текущие записи и загружаем новые
    entry_manager.entries.clear()
    for entry_dict in entries_data:
        entry = Entry.from_json(entry_dict)
        entry_manager.entries.append(entry)

    # Сохраняем - при этом удалятся orphaned файлы
    entry_manager.save()
    return {"status": "success", "message": "Записи сохранены, старые файлы очищены"}


@app.route("/api/delete_entry/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    entry_manager = EntryManager(FOLDER)
    entry_manager.load()

    initial_count = len(entry_manager.entries)
    entry_manager.delete_entry(entry_id)

    if len(entry_manager.entries) < initial_count:
        entry_manager.save()
        return {"status": "success", "message": f"Запись {entry_id} удалена"}
    else:
        return {"status": "error", "message": f"Запись {entry_id} не найдена"}, 404


@app.route("/api/cleanup_orphaned/", methods=["POST"])
def cleanup_orphaned():
    """Очистка orphaned файлов вручную"""
    entry_manager = EntryManager(FOLDER)
    entry_manager.load()

    # Просто вызываем save, который автоматически очистит orphaned файлы
    entry_manager.save()

    return {"status": "success", "message": "Orphaned файлы очищены"}


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)