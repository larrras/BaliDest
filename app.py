
import os
from os.path import join, dirname
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, redirect,url_for
from pymongo import MongoClient
import requests
import jwt
from datetime import datetime,timedelta
import hashlib
from werkzeug.utils import secure_filename


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")

# client = MongoClient(MONGODB_URI)

# db = client[DB_NAME]

client = MongoClient('mongodb+srv://randhyar955:Ardiansyah955@cluster0.vr2df0r.mongodb.net/?retryWrites=true&w=majority')
db = client.dbbalidest

app=Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] =True
app.config['UPLOAD_FOLDER'] = './static/profiL_admin'

SECRET_KEY = "BALIDEST"

# route ke home
@app.route('/')
def home_user():
    token_receive = request.cookies.get('mytoken')
    try:
        payload =jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'id':payload['id']})
        return render_template('home.html', nickname = user_info['nick'])
    except jwt.ExpiredSignatureError :
        return redirect(url_for('login', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError :
        return redirect(url_for('login', msg="Login, yuk!"))

# route ke login 
@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

# route api login
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form.get('id_give')
    pw_receive = request.form.get('pw_give')
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({
        'id' : id_receive,
        'pw' : pw_hash,
    })

    if result is not None:
        payload = {
            'id' : id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60)
        }
        token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
        return jsonify({'result':'success','token':token})
    else :
        return jsonify({'result':'fail', 'msg': 'Coba gunakan ID yang lain, yuk!'})


# route ke register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form.get('id_give')
    pw_receive = request.form.get('pw_give')
    nickname_receive = request.form.get('nickname_give')
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    if db.user.find_one({'id' : id_receive,}):
        return jsonify({'message': 'Maaf, ya. ID telah terdaftar!'}) 
    db.user.insert_one({
        'id' : id_receive,
        'pw' : pw_hash,
        'nick' : nickname_receive
    })
    return jsonify({'result': 'success'})

@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.encode(token_receive,SECRET_KEY,algorithms=['HS256'])
        print(payload)
        user_info = db.user.find_one({'id':payload('id')},{'_id':0})
        return jsonify({'result':'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError: 
        msg="Login Sudah Kadaluarsa"
        return jsonify({'result':'fail','msg':msg})
    except jwt.exceptions.DecodeError:
        msg="Login, yuk!"
        return jsonify({'result':'fail','msg':msg})

import hashlib

# route home_admin
@app.route('/home')
def home_admin():
    token_receive = request.cookies.get('admintoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        admin_info = db.admin.find_one({'id': payload['id']})
        if admin_info:
            return render_template('homeadm.html', admin_info=admin_info)
        else:
            return redirect(url_for('admin', msg="Admin tidak ditemukan"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for('admin', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('admin', msg="Login, yuk!"))

# login admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        id_receive = request.form['id_give']
        pw_receive = request.form['pw_give']
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.admin.insert_one({
            'id' : id_receive,
            'pw' : pw_hash
        })
        return redirect(url_for('admin_login', id_give=id_receive))
    return render_template('loginadmin.html')

# login api admin
@app.route('/api/admin', methods=['POST'])
def admin_login():
    id_receive = request.form.get('id_give')
    pw_receive = request.form.get('pw_give')

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    admin_info = db.admin.find_one({'id': id_receive, 'pw': pw_hash})
    if admin_info:
        token = jwt.encode({'id': id_receive}, SECRET_KEY, algorithm='HS256')
        return jsonify({'result':'success','token':token})  # Mengubah token menjadi string sebelum mengirimkan respons
    else:
        return jsonify({'result': 'failed', 'message': 'Login gagal'})

# route input
@app.route('/input/destinasi')
def input_destinasi():
    balidest = list(db.balides.find({}, {'_id': False}))
    return jsonify({'balidest': balidest})

@app.route('/input/destinasi', methods=['POST'])
def destinasi_input():
    judul = request.form.get('judul_give')
    desc = request.form.get('desc_give')

    # Menerima file
    today =datetime.now()
    mytime = today.strftime('%Y-%M-%d-%H-%M-%S')

    file = request.files["file_give"]
    # # Selanjutnya, mari buat nama file baru menggunakan function datetime
    extension = file.filename.split('.')[-1] #untuk memisahkan tanda titik .jpg
    filename = f'file-{mytime}.{extension}'
    # # Mari gunakan nama file baru tersebut dan ekstensi file original lalu save file nya
    save_to =f'static/{filename}'
    file.save(save_to)

    time = today.strftime('%Y-%M-%d')
    # Simpan data ke MongoDB
    db.balides.insert_one({
        'file':filename,
        'judul': judul,
        'desc': desc,
        'time': time,
    })
    return jsonify({'msg': 'POST request!'})

@app.route('/update_destinasi', methods=['GET','POST'])
def updatedns():
    balidest = list(db.balides.find({}))
    for bali in balidest :
        bali["_id"] = str(bali['_id'])
    return render_template('homeadm.html',balidest=balidest)

@app.route('/update_destinasi/api', methods=['POST'])
def update_destinasi():
    token_receive = request.cookies.get('admintoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        admin_id = payload['_id']
        id = request.args.get("id")
        judul_give = request.form['judul_give']
        desc_give = request.form['desc_give']
        
        id = request.form['id']
        balidest = db.balides.find_one({"_id": ObjectId(id)})
        balidest["_id"] = str(balidest["_id"])
        new_doc = {"judul": judul_give, "desc": desc_give}
        return render_template('updateds.html', balidest=balidest)
        

        if "file_give" in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            mytime = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = f"updatenya-{mytime}.{extension}"
            save_to = f'static/{file_path}'
            file.save(save_to)
            new_doc["file_pic"] = filename
            new_doc["file_real"] = file_path

        db.balides.update_one({"_id": ObjectId(id), "admin_info._id": admin_id}, {'$set': new_doc})
        return redirect('/home')
        return jsonify({'message': 'Data destinasi berhasil diperbarui'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token sudah kadaluarsa'})
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token tidak valid'})


if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)