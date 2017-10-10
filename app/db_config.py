from app import app
from flaskext.mysql import MySQL
def config_db():
    #from testpython import printhello
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'br4cruta'
    app.config['MYSQL_DATABASE_DB'] = 'AAmeetings'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    mysql.init_app(app)
    return mysql
