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

#ruta inicial
@app.route("/")
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM eventos")
    data = cursor.fetchall()
    return render_template("index.html", evento=data)


#rutas de inicio de sesion
@app.route("/login", methods=["POST"])
def login():
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
            return redirect(url_for(".reciente"))
        else:
            return render_template("index.html")

    #ruta que lleva al registro
@app.route("/irRegistro", methods=["POST"])
def irRegistro():
    if request.method == "POST":
        return render_template("registro.html")

#ruta de cerrar sesion
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('idregistro', None)
    session.pop('correo', None)
    return redirect(url_for('index'))

#ruta de registro
@app.route("/registro", methods=["POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]
        ocupacion = request.form["ocupacion"]
    elif request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO registro (nombre,apellido,edad,correo,contraseña,ocupacion)VALUES (%s,%s,%s,%s,%s,%s)", (nombre,apellido,edad,correo,contraseña,ocupacion))
        mysql.connection.commit()
        return redirect(url_for(".index"))
    
#Aqui estan todas la rutas de eventos

@app.route("/home")
def eventos():
    idregistro = session['idregistro']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM eventos where idregistro = %s", (idregistro,))
    data = cursor.fetchall()
    return render_template("home.html", eventos=data)


#ruta pata dirigirse a agregar
@app.route("/agregarlink")
def agregar():
    return render_template("agregarEvento.html")
#ruta para agregar evento
@app.route("/agregarEvento", methods=["POST"])
def agregarEvento():
        if request.method == "POST":
            descripcion = request.form["descripcion"]
            hora = request.form["hora"]
            fecha = request.form["fecha"]
            lugar = request.form["lugar"]
            idregistro = session["idregistro"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO eventos (descripcion,hora,fecha,lugar,idregistro) VALUES (%s,%s,%s,%s,%s)", (descripcion,hora,fecha,lugar,idregistro))
            mysql.connection.commit()
            return redirect(url_for('.eventos'))
            
#ruta para editar evento segun la session
@app.route("/edit/<id>")
def edit_evento(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE idevento = {0}'.format(id))
    data = cursor.fetchall()
    return render_template('editarEventos.html', evento = data[0])
#ruta para editar evento
@app.route('/update/<id>', methods=["POST"])
def update(id):
    if request.method == 'POST':
        descripcion = request.form["descripcion"]
        hora = request.form["hora"]
        fecha = request.form["fecha"]
        lugar = request.form["lugar"]
        cursor = mysql.connection.cursor()
        cursor.execute("""
        UPDATE eventos SET
            descripcion = %s,
            hora = %s,
            fecha = %s,
            lugar = %s
        WHERE idevento = %s""", (descripcion,hora,fecha,lugar,id))
        mysql.connection.commit()
        return redirect(url_for('.eventos'))

#ruta para borrar evento
@app.route("/delete/<string:id>")
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM eventos WHERE idevento = {0}".format(id))
    mysql.connection.commit()
    return redirect(url_for('.eventos'))
@app.route("/recientes")
def reciente():
    idregistro = session["idregistro"]
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT * FROM eventos 
                        WHERE fecha > NOW() and idregistro=%s
                        ORDER BY fecha 
                        LIMIT 3""", (idregistro,))
    data = cursor.fetchall()
    return render_template("eventoreciente.html", ultimos=data)


#ir rutas filtar
@app.route("/irhora")
def irhoras():
    return render_template("horas.html")

@app.route("/irfecha")
def irfechas():
    return render_template("fechas.html")

@app.route("/irlugar")
def irlugar():
    return render_template("lugar.html")

@app.route("/irdescripcion")
def irdescripcion():
    return render_template("descripcion.html")



#rutas filtar
@app.route("/hora", methods=['POST'])
def horas():
    hora = request.form["hora"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE hora = %s',(hora,))
    data = cursor.fetchall()
    return render_template("horas.html", horas=data)
    
@app.route("/fecha", methods=['POST'])
def fechas():
    fecha = request.form["fecha"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE fecha = %s',(fecha,))
    data = cursor.fetchall()
    return render_template("fechas.html", fechas=data)

@app.route("/lugar", methods=['POST'])
def lugar():
    lugar = request.form["lugar"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE lugar = %s',(lugar,))
    data = cursor.fetchall()
    return render_template("lugar.html", lugar=data)

@app.route("/descripcion", methods=['POST'])
def descripcion():
    descripcion = request.form["descripcion"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE descripcion = %s',(descripcion,))
    data = cursor.fetchall()
    return render_template("descripcion.html", descripcion=data)



#Aqui estan todas la rutas de notas
@app.route("/notas")
def notas():
    idregistro = session['idregistro']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM notas where idregistro = %s", (idregistro,))
    data = cursor.fetchall()
    return render_template("notas.html", notas=data)

#ruta pata dirigirse a agregar
@app.route("/notanueva")
def irNota():
    return render_template("agregarNota.html")

#ruta para agregar Notas
@app.route("/agregarnotas", methods=["POST"])
def agregarNota():
        if request.method == "POST":
            nombre = request.form["nombre"]
            descripcion = request.form["descripcion"]
            idregistro = session["idregistro"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO notas (nombre,descripcion,idregistro) VALUES (%s,%s,%s)", (nombre,descripcion,idregistro))
            mysql.connection.commit()
            return redirect(url_for('.notas'))
#ruta para editar evento segun la session
@app.route("/editnota/<id>")
def edit_nota(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM notas WHERE idnotas = {0}'.format(id))
    data = cursor.fetchall()
    return render_template('editarNota.html', nota = data[0])

#ruta para editar notas
@app.route('/updatenota/<id>', methods=["POST"])
def updatenota(id):
    if request.method == 'POST':
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        cursor = mysql.connection.cursor()
        cursor.execute("""
        UPDATE notas SET
            nombre = %s,
            descripcion = %s
        WHERE idnotas = %s""", (nombre,descripcion,id))
        mysql.connection.commit()
        return redirect(url_for('.notas'))

#ruta para borrar nota
@app.route("/deletenota/<string:id>")
def deletenota(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM notas WHERE idnotas = {0}".format(id))
    mysql.connection.commit()
    return redirect(url_for("notas"))

#calendario
@app.route("/calendario")
def calendario():
    return render_template("calendario.html")

if __name__ == "__main__":
    app.run(port= 3000, debug=True)