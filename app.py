from flask import Flask, request
import os

app = Flask(__name__)

FILE_PATH = "data.txt"

@app.post("/write")
def write_data():
    data = request.json.get("text", "")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(data)
    return "Saved"

@app.get("/read")
def read_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "فایلی وجود ندارد"
