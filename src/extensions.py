from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager

conexion = MySQL()
jwt = JWTManager()