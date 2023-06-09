
# import os
# from os.path import join, dirname
# from dotenv import load_dotenv

<<<<<<< HEAD
from flask import Flask, render_template, request, jsonify, redirect,url_for
=======
from flask import Flask, render_template, request, jsonify, redirect, url_for
>>>>>>> f60d08e2ba6b8abc428db2bcdcafdee6129014af
from pymongo import MongoClient
import requests
import jwt
from datetime import datetime,timedelta
import hashlib

# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")

# client = MongoClient(MONGODB_URI)

# db = client[DB_NAME]

client = MongoClient('mongodb+srv://randhyar955:Ardiansyah955@cluster0.vr2df0r.mongodb.net/?retryWrites=true&w=majority')
db = client.dbbalidest

app=Flask(__name__)

SECRET_KEY = "BALIDEST"
# route ke home

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload =jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'id':payload['id']})
        return render_template('home.html', nickname =user_info['nick'])
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
<<<<<<< HEAD
            'exp': datetime.utcnow() + timedelta(seconds=60)
=======
            'exp': datetime.utcnow() + timedelta(seconds=180)
>>>>>>> f60d08e2ba6b8abc428db2bcdcafdee6129014af
        }
        token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
        return jsonify({'result':'success','token':token})
    else :
        return jsonify({'result':'fail', 'msg': 'Coba gunakan email/password lain, yuk!'})


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
        return jsonify({'message': 'Maaf, ya. Username telah terdaftar!'}) 
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
        userinfo = db.user.find_one({'id':payload('id')},{'_id':0})
        return jsonify({'result':'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError: 
        msg="Login Sudah Kadaluarsa"
        return jsonify({'result':'fail','msg':msg})
    except jwt.exceptions.DecodeError:
        msg="Login, yuk!"
        return jsonify({'result':'fail','msg':msg})
    

<<<<<<< HEAD
# login admin
@app.route('/login_admin')
def login_admin(): 
    return render_template('loginadmin.html')


=======
@app.route('/badung',methods=['GET','POST'])
def badung():
    return render_template('badung.html')

@app.route('/gianyar',methods=['GET','POST'])
def gianyar():
    return render_template('gianyar.html')

@app.route('/tabanan',methods=['GET','POST'])
def tabanan():
    return render_template('tabanan.html')

@app.route('/bangli',methods=['GET','POST'])
def bangli():
    return render_template('bangli.html')

@app.route('/karangasem',methods=['GET','POST'])
def karangasem():
    return render_template('karangasem.html')

@app.route('/nusapenida',methods=['GET','POST'])
def nusapenida():
    return render_template('nusapenida.html')
>>>>>>> f60d08e2ba6b8abc428db2bcdcafdee6129014af

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)