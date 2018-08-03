import os
from flask import Flask, flash, request, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/nicole/git/campaign-measurement-webapp/app/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(dict(
    SECRET_KEY="karai_tokusei",
    WTF_CSRF_SECRET_KEY="five_piece_gyoza"
))
Bootstrap(app)

from app import views