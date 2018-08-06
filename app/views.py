from flask import render_template, flash, redirect, request, url_for, send_from_directory
from app import app
import os
from werkzeug.utils import secure_filename
import csv


ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Not correct file type')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('select_variables',
                                    filename=filename))
    return render_template("index.html")

@app.route('/select/<filename>', methods=['GET', 'POST'])
def select_variables(filename):

    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rU") as f:
        d_reader = csv.DictReader(f)
        headers = d_reader.fieldnames

    return render_template("select_variables.html",
                           filename=filename,
                           columns=headers
                           )

@app.route('/calculate_lift', methods=['GET', 'POST'])
def calculate_lift():
    if request.method == "POST":
        var_dict = {
            "user_id": request.form.get("user_id"),
            "user_group": request.form.get("user_group"),
            "user_response": request.form.get("user_response"),
            "campaign_period": request.form.get("campaign_period"),
            "metrics_list": request.form.get("metrics_list"),
        }

    return render_template("calculate_lift.html"
                           )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


# @app.route('/compile/<search_string>')
# def compiler(search_string):
#     # search terms given by user - not yet connected
#     search_string
#
#     # algorithm - none yet
#
#     # get data
#     data_folder = "/Users/nicole/Desktop/cheese/app/data"
#     data = os.listdir(data_folder)
#     for d in [data[0]]:
#         with open(data_folder + "/" + d) as file:
#             d_now = file.read()
#     return render_template("case_view.html", d_now=d_now)
#
#
# @app.route('/review')
# def reviewer():
#     # marked cases
#     marked_cases = ["nicole","nicole","nicole","nicole","nicole"]
#     return render_template("review.html", marked_cases=marked_cases)
