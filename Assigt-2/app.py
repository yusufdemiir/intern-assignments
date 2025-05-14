import gnupg
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
gpg = gnupg.GPG()

#Public key oluşturma
@app.route("/created", methods=["POST"])
def created():
    email = request.form['email']
    password = request.form['password-input']
    input_data = gpg.gen_key_input(name_email = email,
        passphrase = password,
        key_type = 'RSA',
        key_length = 1024)
    print(input_data)
    new_key = gpg.gen_key(input_data)
    print(new_key)
    message = f"{email} adına bir public key oluşturuldu."
    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]
    print(key_list)
    return render_template("index.html", message=message, keys=key_list)

#Sunucu Başlatması
@app.route('/')
def home():
    public_keys = gpg.list_keys()
    key_list = [(key['keyid'], key['uids'][0]) for key in public_keys]
    return render_template("index.html", keys=key_list)

if __name__ == "__main__":
    app.run(debug=True)
