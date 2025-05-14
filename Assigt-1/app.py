from flask import Flask, render_template, request, jsonify
import hashlib
import os
import json

app = Flask(__name__)

#1MB'lık dosya bölme boyutu
split_size = 1024 * 1024 

#Hash Fonksiyonu
def hash_part(input):
    return {
        "md5": hashlib.md5(input).hexdigest(),
        "sha256": hashlib.sha256(input).hexdigest(),
        "sha512": hashlib.sha512(input).hexdigest()
    }

#Ana Sayfa
@app.route('/')
def home():
    return render_template("index.html")

#Dosya Yüklenmesi
@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    content = uploaded_file.read()
    
    #Full File Hash
    full_file_hash = hash_part(content)

    #Split File Hash
    parts = []
    for i in range(0, len(content), split_size):
        part_data = content[i:i+split_size]
        part_hashes = hash_part(part_data)
        part_hashes["part_number"] = i // split_size + 1
        parts.append(part_hashes)
    
    #Sonuçlar
    result = {
        "full_file_hash": full_file_hash,
        "parts": parts
    }
    
    #JSON Çıktısı Yazma
    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

    full_hash = result["full_file_hash"]
    full_text = (
        f"Full File Hashes:\n"
        f"MD5={full_hash['md5']}\n"
        f"SHA256={full_hash['sha256']}\n"
        f"SHA512={full_hash['sha512']}\n\n"
    )
    part_texts = []
    for part in result["parts"]:
        line = (
            f"Split File Hashes:\n"
            f"Part {part['part_number']}:\n"
            f"MD5={part['md5']}\n"
            f"SHA256={part['sha256']}\n"
            f"SHA512={part['sha512']}\n"
        )
        part_texts.append(line)

    final_output = full_text + "\n".join(part_texts)

    return render_template(
    "index.html", 
    final_output=final_output)

    if not uploaded_file:
        return "No file uploaded", 400

if __name__ == "__main__":
    app.run(debug=True)