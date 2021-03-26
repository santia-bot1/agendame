from flask import Flask, render_template, request,redirect, url_for,flash,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

#mysql configuracion
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "contraseña"
app.config["MYSQL_DB"] = "bdagendame"
mysql=MySQL(app)

#configuraciones
app.secret_key = "mysecretkey"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=["POST"])
def login():
    msg =''
    if request.method == 'POST' and 'correo' in request.form and 'contraseña' in request.form:
        correo= request.form['correo']
        contraseña = request.form['contraseña']
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM registro WHERE correo = %s AND contraseña = %s",(correo,contraseña))
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["idregistro"] = account["idregistro"]
            session["correo"] = account["correo"]
            return render_template("home.html")
        else:
            msg="Correo/Contraseña Incorrecto"
    return render_template("index.html",msg=msg)

@app.route("/registro", methods=["POST"])
def registro():
    msg=""
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]
        ocupacion = request.form["ocupacion"]
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO registro (nombre,apellido,edad,correo,contraseña,ocupacion)VALUES (%s,%s,%s,%s,%s,%s)", (nombre,apellido,edad,correo,contraseña,ocupacion))
    mysql.connection.commit()
    flash("Contacto Agregado exitosamente")
    return redirect(url_for(".index"))

@app.route("/registrar", methods=["POST"])
def registrar():
    if request.method == "POST":
        return render_template("registro.html")

if __name__ == "__main__":
    app.run(port= 3000, debug=True)