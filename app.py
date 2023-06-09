
import os
from os.path import join, dirname
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Flask, session, render_template, request, jsonify, redirect,url_for, make_response
from pymongo import MongoClient
from bson import ObjectId
from bson.objectid import ObjectId
import requests
import jwt
from datetime import datetime,timedelta
import hashlib
from werkzeug.utils import secure_filename
import logging



dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

# client = MongoClient('mongodb+srv://randhyar955:Ardiansyah955@cluster0.vr2df0r.mongodb.net/?retryWrites=true&w=majority')
# db = client.dbbalidest

app=Flask(__name__)

app.logger.setLevel(logging.INFO)

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
        return redirect ('/userhomes')
        return render_template('userhomes.html', nickname = user_info['nick'])
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
            'exp': datetime.utcnow() + timedelta(seconds=60*60)
        }
        token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
        return jsonify({'result':'success','token':token})
    else :
        return jsonify({'result':'fail', 'msg': 'Oops! ID/Password kamu salah. Periksa kembali, ya!'})

# route ke logout
@app.route('/logout')
def logout():
    response = make_response(render_template('login.html', msg='Logout berhasil!'))
    response.set_cookie('mytoken', '', expires=0)  # Menghapus cookie token
    return response


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
        return jsonify({'result':'success', 'nickname': user_info['nick']})
    except jwt.ExpiredSignatureError: 
        msg="Login Sudah Kadaluarsa"
        return jsonify({'result':'fail','msg':msg})
    except jwt.exceptions.DecodeError:
        msg="Login, yuk!"
        return jsonify({'result':'fail','msg':msg})



@app.route('/home', methods=['GET', 'POST'])
def home_admin():
    if request.method == 'POST':
        judul = request.form['judul']
        desc = request.form['desc']
    
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    
        file = request.files["file"]
        extension = file.filename.split('.')[-1]
        filename = f'file-{mytime}.{extension}'
        save_to = f'static/{filename}'
        file.save(save_to)
    
        time = today.strftime('%Y-%m-%d')
    
        db.balides.insert_one({
            'file': filename,
            'judul': judul,
            'desc': desc,
            'time': time,
        })
    
    token_receive = request.cookies.get('admintoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        admin_info = db.admin.find_one({'id': payload['id']})
        if admin_info:
            data = list(db.balides.find({}))
            for d in data:
                d['_id'] = str(d['_id'])
                return redirect('/input_destinasi')
            return render_template('homeadminCSS.html', admin_info=admin_info, data=data)
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

# logout admin
@app.route('/admin/logout')
def admin_logout():
    response = make_response(render_template('loginadmin.html',msg="LogOut Berhasil"))
    response.set_cookie('admintoken', '', expires=0)
    return response



@app.route('/input_destinasi')
def input_destinasi():
    balidest = db.balides.find({})
    return render_template('homeadminCSS.html', balidest=balidest)


@app.route('/updates', methods=['GET', 'POST'])
def updates():
    if request.method == "GET":
        id = request.args.get("id")
        data = db.balides.find_one({"_id": ObjectId(id)})
        data["_id"] = str(data["_id"])
        return render_template('updateCSS.html', data=data)

    id = request.form["id"]
    judul = request.form["judul"]
    desc = request.form['desc']
    file_path = ""
    file = request.files.get("file")
    if file:
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        file_path = f'update-{mytime}.{extension}'
        file.save("./static/" + file_path)

    db.balides.update_one({"_id": ObjectId(id)}, {'$set': {"judul": judul, "desc": desc}})
    return redirect('/input_destinasi')


@app.route('/hapus', methods=['POST'])
def hapus():
    id = request.form["id"]
    db.balides.delete_one({"_id": ObjectId(id)})
    return redirect('/input_destinasi')


@app.route('/addcard', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        judul = request.form['judul']
        desc = request.form['desc']
        dayatarik = request.form['dayatarik']
        alamat = request.form['alamat']
        fasilitas = request.form['fasilitas']
        jamoperasional = request.form['jam']
    
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    
        file = request.files["file"]
        extension = file.filename.split('.')[-1]
        filename = f'file-{mytime}.{extension}'
        save_to = f'static/{filename}'
        file.save(save_to)
    
        time = today.strftime('%Y-%m-%d')
    
        db.balides.insert_one({
            'file': filename,
            'judul': judul,
            'desc': desc,
            'time': time,
            'dayatarik': dayatarik,
            'alamat': alamat,
            'fasilitas': fasilitas,
            'jam': jamoperasional

        })
        # return render_template('/ulasan2.html',reviews=reviews)
    
        return redirect('/input_destinasi')
    
    token_receive = request.cookies.get('admintoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        admin_info = db.admin.find_one({'id': payload['id']})
        if admin_info:
            data = list(db.balides.find({}))
            for d in data:
                d['_id'] = str(d['_id'])
            return render_template('addcard.html', data=data)  # Pass the 'data' variable to the template
        else:
            return redirect(url_for('admin', msg="Admin tidak ditemukan"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for('admin', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('admin', msg="Login, yuk!"))

@app.route('/userhomes')
def userhomes():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'id': payload['id']})
        balidest = db.balides.find()  # Mengambil semua data dari koleksi 'balides'

        return render_template('userhomes.html', balidest=balidest, nickname=user_info['nick'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg="Login, yuk!"))


# Lihat Daftar Registrasi
@app.route('/daftar_user')
def daftar_user():
    users = db.user.find()  # Mengambil semua data user dari koleksi 'user'
    return render_template('daftar_user.html', users=users)


# details dari destinasi
@app.route('/details')
def details():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'id': payload['id']})
        if user_info:
            id = request.args.get("id")
            data = db.balides.find_one({"_id": ObjectId(id)})
            review = db.reviews.find({"review_id": id})
            if data:
                data["_id"] = str(data["_id"])
                return render_template('details.html', data=data, review=review,user_info=user_info)
            else:
                return "Destinasi tidak ditemukan"  # Tambahkan penanganan jika destinasi tidak ditemukan
        else:
            return "Pengguna tidak ditemukan"  # Tambahkan penanganan jika pengguna tidak ditemukan
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg="Silakan Login"))


# review
@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'id': payload['id']})
        if user_info:
            if request.method == 'POST':
                judul = request.form.get('judul')
                rating = request.form.get('rating')
                comment = request.form.get('comment')
                review_id = request.form.get('review_id')

                today = datetime.now()
                time = today.strftime('%Y-%m-%d')

                # Simpan review ke dalam database
                review = {
                    'user_id': user_info['id'],
                    'judul': judul,
                    'rating': rating,
                    'comment': comment,
                    'time': time,
                    'review_id': review_id
                }
                db.reviews.insert_one(review)

                return redirect(url_for('details', id=review_id))
            elif request.method == 'GET':
                id = request.args.get("id")
                data = db.balides.find_one({"_id": ObjectId(id)})
                if data:
                    data["_id"] = str(data["_id"])
                    return render_template('details.html', data=data, review=review)
                else:
                    return "Destinasi tidak ditemukan"  # Tambahkan penanganan jika destinasi tidak ditemukan
        else:
            return "Pengguna tidak ditemukan"  # Tambahkan penanganan jika pengguna tidak ditemukan
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg="Login Sudah Kadaluarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg="Silakan Login"))


# Lihat Daftar Review
@app.route('/daftar_review')
def daftar_review():
    reviews = list(db.reviews.find()) # Mengambil semua review user dari koleksi 'reviews'
    return render_template('daftar_review.html', reviews=reviews)

@app.route('/delete_review', methods=['POST'])
def delete_review():
    review_id = request.form["review_id"]
    db.reviews.delete_one({"_id": ObjectId(review_id)})
    return redirect('/daftar_review')


if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)