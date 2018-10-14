from flask import Flask, request, redirect, url_for, render_template, send_file, session, current_app, after_this_request
import os, uuid
import logging
from db.database import init_db, checkLogin, register, addFile, collectFile, userUploads

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

init_db()

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    else:
        success = register(request.form['username'],
                            request.form['password'],
                            request.form['firstName'],
                            request.form['lastName'])
        if success is True:
            return "<script> alert('Signup successful'); window.location.href = '/login'; </script>"
        else:
            return "<script> alert('Email already exists!'); window.history.back(); </script>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        user = checkLogin(request.form['username'], request.form['password'])
        if user is False:
            return "<script> alert('Incorrect credentials'); window.history.back(); </script>"
        else:
            session["user"] = user
            return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Remove the username from the session if it's there
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    userID = session['user']['id']
    if request.method == 'POST':
        if 'files' in request.files:
            url_list = []
            for f in request.files.getlist('files'):
                if f and f.filename != '':
                    id = str(uuid.uuid4())
                    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'],id)
                    os.makedirs(upload_dir)
                    upload_location = os.path.join(upload_dir,f.filename)
                    f.save(upload_location) 
                    addFile(id,f.filename, userID)
                    url_list.append("http://localhost:5000%s" % url_for('download',id=id, filename=f.filename))
                else:
                    logging.error("Something's gone quite badly wrong")

            return render_template('submit.html', **locals())
        else:
            return "<script> alert('Please supply at least one file'); window.history.back(); </script>"
    

@app.route('/download/<id>/<filename>', methods=['GET']) #Landing page
def download(id,filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'],id) 
    fname = str(filename)
    return render_template('download.html', **locals())


@app.route('/download_file/<id>/<filename>')  # This does the actual downloading
def download_file(id,filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'],id)

    file_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'],id,filename)
    file_handle = open(file_path, 'r')
    collectFile(id)

    # NOTE: This below request might not work on Windows
    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
            if not os.listdir(uploads):
                os.rmdir(uploads)
            print('Deleted file (and possibly folder)')
            file_handle.close()

        except Exception as e:
            app.logger.error("Error removing or closing downloaded file handle", e)
        return response

    return send_file(file_path, as_attachment=True)

@app.route('/upload_list', methods = ['GET'])
def uploadList():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirects user to login page
    else:
        username = session['user']['id']
        headers = ["File ID", "Filename", "Collected", "Upload Timestamp", "Download Timestamp"]
        data = userUploads(username)
        return render_template('upload_list.html', **locals())


if __name__ == "__main__":
    app.run(debug=True)