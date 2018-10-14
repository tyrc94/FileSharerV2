import sqlite3
from flask import g, Flask
from pprint import pprint
import logging
app = Flask(__name__)

DATABASE = 'db/database.db'

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    db.row_factory = make_dicts
    return db


def mutate_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
    return True


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def addFile(uid, filename, user, requireLogin = False, expire = None, password = None):
    mutate_db("INSERT INTO OneOffFiles (userId, uid, filename, expire, password, requireLogin, uploadTime) VALUES (?,?,?,?,?,?, datetime('now'))",
        [user, uid, filename, expire, password, requireLogin])
    if requireLogin:
        requireLogin = 1
    else:
        requireLogin = 0 


def userUploads(username):
    #uploads = query_db("SELECT * FROM OneOffFiles WHERE userId = ?", [username])
    uploads = query_db("SELECT uid, filename, collected, uploadTime, downloadTime FROM OneOffFiles WHERE userId = ?", [username])
    if username is None:
        return False
    else:
        return uploads


def collectFile(uid, user = None, requireLogin = False): # Sets the collected file to be True (or 1)
    mutate_db("UPDATE OneOffFiles SET collected = ?, collectedUserId = ?, downloadTime = datetime('now') WHERE uid = ?", (1, user, uid))
    if requireLogin:
        return 1
    else:
        return 0


def checkLogin(username,password):
    user = query_db('SELECT * FROM User WHERE email = ? AND password = ?', (username, password), one=True)
    if user is None:
        return False
    else:
        return user

def getSalt(username):
    salt = query_db('SELECT salt FROM User WHERE email = ?', (username,), one=True)
    if salt is None:
        return None
    else:
        return salt['salt']

def register(username,password,firstName,lastName,salt):
    try:
        user = mutate_db("INSERT INTO User (email, password, firstName, lastName, salt) VALUES (?,?,?,?,?)",
                    (username, password, firstName, lastName, salt))
        return True
    except Exception as e:
        app.logger.error(e)
        return False
    