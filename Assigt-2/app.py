import gnupg
import os
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
gpg = gnupg.GPG(options=['--pinentry-mode', 'loopback'])

#Public key oluşturma
@app.route("/created", methods=["POST"])
def created():
    email = request.form['email']
    password = request.form['password-input']

    input_data = gpg.gen_key_input(name_email = email,
        passphrase = password,
        key_type = 'RSA',
        key_length = 1024)
    
    gpg.gen_key(input_data)

    message = f"{email} adına bir public key oluşturuldu."
    
    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]

    return render_template("index.html", message=message, keys=key_list)

#Encryption İşlemi
@app.route("/encrypt", methods=["POST"])
def encrypt():
    
    #Seçilen emaili çekme
    selected_file = request.files.get("file")
    selected_key = request.form['gpg_key']
    email = None
    for key in gpg.list_keys():
        if key['keyid'] == selected_key:
            email = key['uids'][0]  # örn. 'Mehmet <mehmet@example.com>'
            break
    match_email = re.search(r'<(.+?)>', email)

    #Yüklenen dosyayı kaydetme
    filename = secure_filename(selected_file.filename)
    temp_path = os.path.join("files/uploaded-files", filename)
    selected_file.save(temp_path)
    encrypted_filename = os.path.join("files/encrypted-files", filename + ".gpg")
    
    #Encrypt işlemi
    with open(temp_path, 'rb') as f:
        status = gpg.encrypt_file(
            f,
            recipients=[email],
            output=encrypted_filename
        )
    print(status.ok)
    print(status.stderr)
    message = 'İşlem Başarılı!'

    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]
    return render_template("index.html", keys=key_list, message=message)

#Decrypt işlemi
@app.route("/decrypt", methods=["POST"])
def decrypt():
    
    password = request.form['passphrase']
    selected_file = request.files.get("file")
    filename = secure_filename(selected_file.filename)
    temp_path = os.path.join("files/temp-decrypt", filename)
    selected_file.save(temp_path)
    with open(temp_path, "rb") as f:
        decrypted_data = gpg.decrypt_file(f, passphrase=password)
    original_filename = Path(filename).stem
    output_dir = "files/decrypted-files"
    output_path = os.path.join(output_dir, original_filename)
    with open(output_path, "w", encoding="utf-8") as out_file:
        status = out_file.write(str(decrypted_data.data, encoding="utf-8"))
    
    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]
    return render_template("index.html", keys=key_list)

#Sunucu Başlatması
@app.route('/')
def home():
    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]
    return render_template("index.html", keys=key_list)

if __name__ == "__main__":
    app.run(debug=True)
