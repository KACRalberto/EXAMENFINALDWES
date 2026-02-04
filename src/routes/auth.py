from flask import Blueprint, redirect, url_for, render_template, request, flash, session, jsonify
from extensions import conexion
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from functions import crear_token, getData




auth = Blueprint("auth", __name__, url_prefix="/auth")



@auth.route("/login")
def login_form():
    return render_template("login.html")



@auth.route("/register")
def register_form():
    return render_template("register.html")



@auth.route("/dashboard")
def dashboard():
    token = session.get("user_token")

    if not token:
        return redirect(url_for('auth.register_form'))
    
    try:
        cursor = conexion.connection.cursor()

        query = "SELECT * FROM favoritos WHERE id_user = %s"

        user_id = session.get("user_id")

        cursor.execute(query,(user_id,))

        personajes_favoritos = cursor.fetchall()

    except:
        flash("HUBO UN PROBLEMA")

    return render_template('dashboard.html', personajes_favoritos=personajes_favoritos)



@auth.route("/register", methods=["POST"])
def register_submit():

    email = request.form.get("email", "").strip().lower()
    user_name = request.form.get("user_name", "").strip()
    password_user = request.form.get("password_user", "")
    password_confirm = request.form.get("password_confirm", "")

    if not email or not user_name or not password_user or not password_confirm:
        flash("DEBE RELLENAR TODO EL FORMULARIO DE REGISTRO", "info")
        return redirect(url_for("auth.register_form"))
    
    if len(password_user) < 5:
        flash("LA CONTRASEÑA DEBE SER MAYOR A 4 CARACTERES")
        return redirect(url_for("auth.register_form"))        
    
    if password_confirm != password_confirm:
        flash("LAS CONTRASEÑAS DEBEN COINCIDIR", "info")
        return redirect(url_for("auth.register_form"))
    
    try:

        cursor = conexion.connection.cursor()

        query = "SELECT * FROM users WHERE email = %s"
        
        cursor.execute(query,(email,))

        user_found = cursor.fetchone()

        if user_found:
            flash("USUARIO YA REGISTRADO", "warning")
            return redirect(url_for("auth.register_form"))
        
        if email == "admin@admin.com":
            query = "INSERT INTO users (email,password_user,user_name,rol) VALUES (%s, %s, %s, 'admin')"
        else:
            query = "INSERT INTO users (email,password_user,user_name) VALUES (%s, %s, %s)"

        password_user = generate_password_hash(password_user)

        cursor.execute(query, (email,password_user, user_name))

        conexion.connection.commit()

        query = "SELECT * FROM users WHERE email = %s"
        
        cursor.execute(query,(email,))

        user_found = cursor.fetchone()

        session.clear()

        token = crear_token(email)

        session["user_token"] = token
        session["user_id"] = user_found["id"]
        session["user_name"] = user_found["user_name"]
        session["user_rol"] = user_found.get("rol", "usuario")

        personajes_favoritos = getData()
        print(personajes_favoritos)
        query = "INSERT INTO favoritos (id_personaje, id_user, img_personaje, description_personaje) VALUES (%s,%s,%s,%s)"
        for personaje in personajes_favoritos:

            cursor.execute(query,(personaje["id"],session.get("user_id"),personaje["image"],personaje["name"]))
            ## AQUI LA INFORMACIÓN RELEVANTE PARA MI ES EL NOMBRE xd
            conexion.connection.commit()
        
        session["personajes_favoritos"] = personajes_favoritos
        

        return redirect(url_for('auth.dashboard'))


    except Exception as e:
        print(e)
        flash("OCURRIÓ UN ERROR REGISTRANDO AL USUARIO", "warning")
        return redirect(url_for('auth.register_form'))
    

@auth.route("/login", methods=["POST"])
def login_submit():

    email = request.form.get("email", "").strip().lower()
    password_user = request.form.get("password_user", "")


    if not email or not password_user:
        flash("DEBE RELLENAR TODO EL FORMULARIO DE LOGIN", "info")
        return redirect(url_for("auth.login_form"))
    
    try:

        cursor = conexion.connection.cursor()

        query = "SELECT * FROM users WHERE email = %s"
        
        cursor.execute(query,(email,))

        user_found = cursor.fetchone()

        if not user_found:
            flash("USUARIO INCORRECTO", "warning")
            return redirect(url_for("auth.login_form"))
    
        password_ok = check_password_hash(user_found["password_user"], password_user)

        session.clear()

        token = crear_token(email)

        session["user_token"] = token
        session["user_id"] = user_found["id"]
        session["user_name"] = user_found["user_name"]
        session["user_rol"] = user_found.get("rol", "usuario")

        return redirect(url_for('auth.dashboard'))


    except Exception as e:
        print(e)
        flash("OCURRIÓ UN ERROR INICIANDO SESIÓN", "warning")
        return redirect(url_for('auth.login_form'))

@auth.route("/auth")
def IMADMIN():
    return render_template("autorizado.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.register_form'))


@auth.route("/token")
def API_rest(): 

        rol = session.get("user_rol","")
        token = session.get("user_token","")

        if rol != "admin" or not token:
            flash("ACCESO NO PERMITIDO", "danger")
            return redirect(url_for('auth.dashboard'))

        return jsonify({"token":token})



@auth.route("/api/admin")
@jwt_required()
def show_data():

        try:
            cursor = conexion.connection.cursor()

            query = "SELECT * FROM favoritos"

            cursor.execute(query)

            personajes_favoritos = cursor.fetchall()

            return jsonify({"DATA": personajes_favoritos})

        except Exception as e:
            print(e)
            return jsonify({"algo fue mal" : "rana"})
        



@auth.route("/api/admin", methods=["POST"])
@jwt_required()
def post_data():


        data = request.get_json()
        id_personaje = data["id_personaje"]
        id_user = data["id_user"]
        img_personaje = data["img_personaje"]
        description_personaje = data["description_personaje"]

        try:
            cursor = conexion.connection.cursor()

            query = "INSERT INTO favoritos (id_personaje, id_user, img_personaje, description_personaje) VALUES (%s,%s,%s,%s)"

            cursor.execute(query,(id_personaje, id_user, img_personaje, description_personaje))

            conexion.connection.commit()

            return jsonify({"DATA ACTUALIZADA MEDIANTE POST": "TODO OK"})

        except Exception as e:
            print(e)
            return jsonify({"algo fue mal" : "rana"})
        

@auth.route("/api/admin", methods=["PUT"])
@jwt_required()
def change_data():


        data = request.get_json()
        id_personaje = data["id_personaje"]
        id_user = data["id_user"]
        img_personaje = data["img_personaje"]
        description_personaje = data["description_personaje"]

        try:
            cursor = conexion.connection.cursor()

            query = "UPDATE favoritos SET id_personaje =%s, id_user =%s, img_personaje =%s, description_personaje =%s"

            cursor.execute(query,(id_personaje, id_user, img_personaje, description_personaje))

            conexion.connection.commit()

            return jsonify({"DATA ACTUALIZADA MEDIANTE PUT": "TODO OK"})

        except Exception as e:
            print(e)
            return jsonify({"algo fue mal" : "rana"})
        
    

@auth.route("/api/admin", methods=["DELETE"])
@jwt_required()
def delete_data():


        data = request.get_json()
        id_personaje = data["id_personaje"]
        id_user = data["id_user"]
        try:
            cursor = conexion.connection.cursor()

            query = "DELETE FROM favoritos WHERE id_personaje =%s AND id_user =%s"

            cursor.execute(query,(id_personaje,id_user))

            conexion.connection.commit()

            return jsonify({"DATA ACTUALIZADA MEDIANTE DELETE": "TODO OK"})

        except Exception as e:
            print(e)
            return jsonify({"algo fue mal" : "rana"})