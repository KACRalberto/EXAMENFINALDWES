from flask import Flask, redirect, url_for, render_template
from os import getenv
from dotenv import load_dotenv
from extensions import conexion, jwt
from datetime import timedelta
from routes.auth import auth
load_dotenv()




app = Flask(__name__)

app.secret_key =  getenv("JWT_SECRET_TOKEN")

app.config["MYSQL_USER"] = getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = getenv("MYSQL_PASSWORD")
app.config["MYSQL_HOST"] = getenv("MYSQL_HOST")
app.config["MYSQL_DB"] = getenv("MYSQL_DB")
app.config["MYSQL_CURSORCLASS"] = getenv("MYSQL_CURSORCLASS")

app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_TOKEN")
app.config["JWT_TOKEN_ACCESS_EXPIRES"] = timedelta(minutes=20)

conexion.init_app(app)
jwt.init_app(app)

app.register_blueprint(auth)

@app.route("/")
def index():
    return redirect(url_for('auth.dashboard'))

@app.errorhandler(404)
def error(error):
    return render_template("404.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')