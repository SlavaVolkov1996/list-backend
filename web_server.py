from flask import Flask, request
from resources import EntryManager, Entry
import os

FOLDER = os.environ.get('FOLDER', '/app/data')

app = Flask(__name__)


@app.route("/api/entries/")
def get_entries():
    entry_manager = EntryManager(FOLDER)
    entry_manager.load()
    # Преобразуем каждую запись в dict и возвращаем список
    return [entry.json() for entry in entry_manager.entries]


@app.route("/api/save_entries/", methods=["POST"])
def save_entries():
    entry_manager = EntryManager(FOLDER)
    entries_data = request.get_json()
    for entry_dict in entries_data:
        entry = Entry.from_json(entry_dict)
        entry_manager.entries.append(entry)
    entry_manager.save()
    return {"status": "success"}


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
