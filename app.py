from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set".format(name)
        raise Exception(message)

POSTGRESQL_URL = "127.0.0.1:5432"
POSTGRESQL_USER = "postgres"
POSTGRESQL_PW = "n0m3l0"
POSTGRESQL_DATABASE = "simpleComments"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRESQL_USER, pw=POSTGRESQL_PW, url=POSTGRESQL_URL, db=POSTGRESQL_DATABASE)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = SQLAlchemy(app)

# Modelo de la tabla Comments en la base de datos.
class Comments(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    comment = database.Column(database.String(50))

# Modelo de la tabla Usuarios en la base de datos.
class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(50), unique=True, nullable=False)
    password = database.Column(database.String(80), nullable=False)

@app.route("/")
def index():
    msg = "Saludos desde el backend!!"
    data = ["footer", "header", "body", "template"]
    return  render_template("index.html", msg=msg, list=data)

@app.route("/insert/default")
def insert_default():
    new_comment = Comments(comment='Insertar a la base de datos 2')
    database.session.add(new_comment)
    database.session.commit()

    return "El comentario ha sido añadido a la base de datos"

@app.route("/select/default")
def select_default():
    info = Comments.query.filter_by(id=1).first()
    print(info.comment)

    return "Se ha hecho una consulta a la base de datos con el id = {}".format(info.id)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = Users(username=request.form["username"], password=hashed_pw)
        database.session.add(new_user)
        database.session.commit()

        return "Se ha registrado el usuario exitosamente."

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        """
        Si se cambia el orden de los parámetros en la función 'check_password_hash'
        no funciona. CHECHAR ESTO
        """
        if user and check_password_hash(user.password, request.form["password"]):
            return "Has iniciado sesión"
        return "Tus credenciales son inválidas, revisa y logeate de nuevo"
    return render_template("login.html")

if __name__ == "__main__":
    database.create_all()
    app.run(debug=True)