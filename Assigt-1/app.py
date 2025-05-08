from flask import Flask, render_template, request, jsonify
import hashlib
import os
import json

app = Flask(__name__)

#1MB'lık dosya bölme boyutu
split_size = 1024 * 1024 

#Hash Fonksiyonu
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
    
    #Full File Hash
    full_file_hash = hash_chunk(content)

    #Split File Hash
    chunks = []
    for i in range(0, len(content), split_size):
        chunk_data = content[i:i+split_size]
        chunk_hashes = hash_chunk(chunk_data)
        chunk_hashes["chunk_number"] = i // split_size + 1
        chunks.append(chunk_hashes)
    
    result = {
        "full_file_hash": full_file_hash,
        "chunks": chunks
    }

    #Split File Hash
    
    #JSON Çıktısı Yazma
    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

    full_hash = result["full_file_hash"]
    full_text = (
        f"Full File Hashes:\n"
        f"MD5={full_hash['md5']}\n"
        f"SHA256={full_hash['sha256']}\n"
        f"SHA512={full_hash['sha512']}\n"
    )
    chunk_texts = []
    for chunk in result["chunks"]:
        line = (
            f"Chunk {chunk['chunk_number']}: "
            f"MD5={chunk['md5']}, "
            f"SHA256={chunk['sha256']}, "
            f"SHA512={chunk['sha512']}"
        )
        chunk_texts.append(line)
        chunk_texts.append('\n')

    
    return render_template(
    "index.html", 
    text_output_full=full_text,
    text_output_split=chunk_texts)

    if not uploaded_file:
        return "No file uploaded", 400

if __name__ == "__main__":
    app.run(debug=True)