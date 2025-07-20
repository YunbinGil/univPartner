from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    
     # DB 연결 설정
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'  # 너가 워크벤치에서 로그인할 때 쓰는 유저
    app.config['MYSQL_PASSWORD'] = '4564'  # 설치할 때 만든 비번
    app.config['MYSQL_DB'] = 'univpartner_db'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # 결과를 dict 형태로

    app.secret_key = 'it_is_a_secret'

    mysql.init_app(app)  # Flask 앱에 MySQL 연결 등록

    from .routes import main
    app.register_blueprint(main) #routes.py에서 가져온 라우터 묶음을 등록

    return app