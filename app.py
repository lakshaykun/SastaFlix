from flask import Flask, request, render_template, redirect, session
from pymongo import MongoClient
import os
import random

client = MongoClient(
    "mongodb+srv://lakshu1000:lakshay1920@mlprojects.n13dkun.mongodb.net/",
    serverSelectionTimeoutMS=50000,  # Increase the timeout
    connectTimeoutMS=50000,
    socketTimeoutMS=50000
)
db = client["SastaFlix"]
users = db["users"]
anime_list = db["anime"]

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_search_results(query):
    results = list(anime_list.find({'ename': {'$regex': query, '$options': 'i'}}))[:20]
    return results

def get_home_results():
    results = list(anime_list.find())
    results = random.sample(results, len(results))[:20]
    return results

@app.route('/')
def start():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return redirect('/login')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    results = get_search_results('attack on titan')
    return render_template('home.html', results = results)

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect('/home')
    return render_template('login.html')

@app.route('/register')
def register():
    if 'user_id' in session:
        return redirect('/home')
    return render_template('register.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')
    details = users.find_one({"email" : email, "password":password})
    if details == None:
        return redirect('/register')
    else:
        session['user_id'] = details["email"]
        session['user_name'] = details["name"]
        return redirect('/home')

@app.route('/registration', methods=['POST'])
def registration():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    details = users.find_one({"email":email})
    if details == None:
        users.insert_one({"name":name, "email":email, "password":password})
        return redirect('/login')
    else:
        return redirect('/register')

@app.route('/logout')
def logout():
    session.pop("user_id")
    return redirect("/")

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('prof.html', email = session['user_id'], name = session['user_name'])

@app.route('/search', methods = ["POST"])
def search():
    search_query = request.form.get('query')
    results = get_search_results(search_query)
    return render_template('home.html', results = results)

if __name__ == '__main__':
    app.run(debug=True)
