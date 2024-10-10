from flask import Flask
from app.routes import products_bp
from app.config import DBconfig
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config.from_object(DBconfig)

    app.db = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )

    app.register_blueprint(products_bp)
    
    return app