from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
import os


app = Flask(__name__)

# Connect to MongoDB : colle la clé MONGO entre les parenthese de Mongoclient()
# Voir la ressource https://lp-magicmakers.fr/accueil/ressources-makers/menu-flask/base-de-donnees/brancher-sa-bdd/
client = pymongo.MongoClient("mongodb+srv://patricknumber2222_db_user:taw25tQICDdGc614@articles.nhgkqeg.mongodb.net/?retryWrites=true&w=majority&appName=Articles")
db = client["mm_site"] #ici c'est le nom de ta base de donnée

app.secret_key = "taw25tQICDdGc614"
#route pour afficher le template index.html
@app.route("/")
def index():
    annonce_data = list(db["Article"].find({}))
    return render_template('index.html', annonces = annonce_data)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q','').strip()
    if query == "":
        res = list(db["Article"].find({}))
    else:
        res = list(db["Article"].find({
            "$or":[
                {"Title" : {"$regex":query,"$options":"i"}},
                {"Description" : {"$regex":query,"$options":"i"}},
                {"User" : {"$regex":query,"$options":"i"}}
            ]
        }))
    return render_template('search_result.html',annonces = res, query=query)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db_users = db["User"]
        user = db_users.find_one({'User_id': request.form['user']})

        if user:
            if request.form['password'] == user['User_password']:

                session['user'] = request.form['user']

                return redirect(url_for('index'))
            else:
                return render_template('login.html', erreur="Incorrect Password")
        else:
            return render_template('login.html', erreur="Incorrect User")
    else:

        return render_template("login.html")

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        db_users = db['User']
        if not db_users.find_one({'User_id':request.form['user']}):
            if  request.form['password']==request.form['confirm_password']:
                db_users.insert_one({
                    'User_id':request.form['user'],
                    'User_password':request.form['password']
                })
                session['user'] = request.form['user']
                return redirect(url_for('index'))
            else:
                return render_template('register.html', erreur="Passwords not identical")
        else:
            return render_template('register.html', erreur="User already exists")
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/publish', methods = ["POST","GET"])
def publish():
    if 'user' not in session:
        return render_template('register.html')
    if request.method == "POST":
        db_articles = db["Article"]
        if request.form['title'] and request.form['content']:
            db_articles.insert_one({
                'Title':request.form['title'],
                'Image':request.form['image'],
                'Description':request.form['content'],
                'User': 'submitted by ' + session['user']
            })
        return redirect(url_for('index'))
    else:
        return render_template('publish.html', erreur = "Fill in all the mandatory fields")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)