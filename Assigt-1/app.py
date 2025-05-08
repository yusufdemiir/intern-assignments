from flask import Flask, render_template, request, jsonify
import hashlib
import os
import json

app = Flask(__name__)

#1MB'lık dosya bölme boyutu
split_size = 1024 * 1024 

def hash_chunk(input):
    return {
        "md5": hashlib.md5(input).hexdigest(),
        "sha256": hashlib.sha256(input).hexdigest(),
        "sha512": hashlib.sha512(input).hexdigest()
    }

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    
    content = uploaded_file.read()
    full_file_hash = hash_chunk(content)
    result = {
        "full_file_hash": full_file_hash
    }

    #JSON Çıktısı Yazma
    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

    return render_template("index.html", json_output=json.dumps(result, indent=4))

    if not uploaded_file:
        return "No file uploaded", 400


if __name__ == "__main__":
    app.run(debug=True)