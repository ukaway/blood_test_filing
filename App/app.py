from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.utils import secure_filename
from datetime import datetime
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from pytesseract import Output
import os

app = Flask(__name__)
username = ''
password = ''
host = ''
database = 'OnlineMed'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://{username}:{password}@{host}/{database}?driver=ODBC+Driver+18+for+SQL+Server'
db = SQLAlchemy(app)


class Patient(db.Model):
    __tablename__ = 'Patient'
    PatientID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=True)
    DateOfBirth = db.Column(db.Date, nullable=True)
    Gender = db.Column(db.CHAR(1), nullable=True)


class Test(db.Model):
    __tablename__ = 'Test'
    TestID = db.Column(db.Integer, primary_key=True)
    TestName = db.Column(db.String(100), nullable=True)
    Description = db.Column(db.Text, nullable=True)
    NormalRange = db.Column(db.String(100), nullable=True)
    Unit = db.Column(db.String(10), nullable=True)


class PatientTest(db.Model):
    __tablename__ = 'PatientTest'
    PatientTestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), nullable=False)
    TestDate = db.Column(db.Date, nullable=False)
    Comments = db.Column(db.Text, nullable=True)


class TestValue(db.Model):
    __tablename__ = 'TestValue'
    ResultID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientTestID = db.Column(db.Integer, nullable=False)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), nullable=False)
    TestID = db.Column(db.Integer, db.ForeignKey('Test.TestID'), nullable=True)
    TestDate = db.Column(db.Date, db.ForeignKey('PatientTest.TestDate'), nullable=True)
    ResultValue = db.Column(db.Numeric(10, 2), nullable=True)


class ImagePath(db.Model):
    __tablename__ = 'ImagePath'
    ImageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FileName = db.Column(db.String(255), nullable=False)
    FilePath = db.Column(db.String(255), nullable=False)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'))
    PatientTestID = db.Column(db.Integer, db.ForeignKey('PatientTest.PatientTestID'))


# Running on http://127.0.0.1:5000
@app.route('/test_db')
def test_db():
    try:
        sql = text("SELECT 1")
        result = db.session.execute(sql)
        return 'Database Connected!'
    except Exception as e:
        return 'Database Connection Failed: ' + str(e)


@app.route('/')
def index():
    return render_template('/index.html')


@app.route('/test_list', methods=['POST'])
def test_list():
    patient_id = request.form['patient_id']
    patient_test_list = PatientTest.query.filter_by(PatientID=patient_id).all()
    if patient_test_list:
        patient = Patient.query.filter_by(PatientID=patient_id).first()
        patient_name = f"{patient.FirstName} {patient.LastName}"
        return render_template('/test_list.html',
                               patient_id=patient_id, patient_name=patient_name,
                               patient_test_list=patient_test_list)
    return render_template('no_tests_found.html', patient_id=patient_id)


@app.route('/test_result_form')
def test_result_form():
    tests = Test.query.all()
    return render_template('/form.html', tests=tests)


@app.route('/save_test_result', methods=['POST'])
def save_test_result():
    patient_id = request.form['patient_id']
    test_date = request.form['test_date']
    file_path = request.form['file_path']
    file_name = request.form['file_name']
    comments = request.form.get('comments')

    test_date_obj = datetime.strptime(test_date, '%Y-%m-%d')

    new_patient_test = PatientTest(PatientID=patient_id, TestDate=test_date_obj, Comments=comments)
    db.session.add(new_patient_test)
    db.session.commit()
    patient_test_id = new_patient_test.PatientTestID

    for test in Test.query.all():
        result_value = request.form.get(f'result_{test.TestID}')
        if result_value:  # Only insert if there's a result value
            new_test_value = TestValue(
                PatientTestID=patient_test_id,
                PatientID=patient_id,
                TestID=test.TestID,
                TestDate=test_date_obj,
                ResultValue=result_value
            )
            db.session.add(new_test_value)

    if file_path:
        new_image_path = ImagePath(
            FileName=file_name,
            FilePath=file_path,
            PatientID=patient_id,
            PatientTestID=patient_test_id
        )
        db.session.add(new_image_path)
    db.session.commit()

    return redirect(url_for('show_test_result', patient_test_id=patient_test_id))


@app.route('/show_test_result/<int:patient_test_id>')
def show_test_result(patient_test_id):
    tests = Test.query.all()
    test_values = TestValue.query.filter_by(PatientTestID=patient_test_id).all()
    patient_test = PatientTest.query.filter_by(PatientTestID=patient_test_id).first()
    test_date = patient_test.TestDate
    patient_id = patient_test.PatientID
    patient = Patient.query.filter_by(PatientID=patient_id).first()
    patient_name = f"{patient.FirstName} {patient.LastName}"
    image = ImagePath.query.filter_by(PatientTestID=patient_test_id).first()
    if image:
        image_url = url_for('static', filename=image.FilePath)
    else:
        image_url = None  # image DNE

    return render_template('test_result.html',
                           patient_id=patient_id, patient_name=patient_name, tests=tests, patient_test=patient_test,
                           test_values=test_values, test_date=test_date, image_url=image_url)


@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    tests = Test.query.all()
    if request.method == 'POST':
        image = request.files['image']
        ocr_enabled = request.form.get('ocr_enabled') == 'on'
        if image:
            filename = secure_filename(image.filename)
            file_path = os.path.join('static', 'images', filename)
            image.save(file_path)
            # URL
            image_url = url_for('static', filename=os.path.join('images', filename))
            # Perform OCR if enabled
            if ocr_enabled:
                ocr_results = perform_ocr(file_path)
            else:
                ocr_results = None
            return render_template('form_with_uploaded_image.html',
                                   image_url=image_url, file_path='images/' + filename,
                                   file_name=filename, tests=tests, ocr_results=ocr_results)
    return render_template('form.html', tests=tests)


def perform_ocr(image_path):
    image = Image.open(image_path)
    image = image.convert("L")  # grayscale
    # image = image.filter(ImageFilter.MedianFilter())  # noise
    enhancer = ImageEnhance.Contrast(image)  # contrast
    image = enhancer.enhance(3)
    image = image.point(lambda x: 0 if x < 60 else 255)
    d = pytesseract.image_to_data(image, output_type=Output.DICT)
    ocr_results = []
    for i in range(len(d['text'])):
        if int(d['conf'][i]) > 40:  # Confidence threshold
            ocr_result = {
                'x': d['left'][i],
                'y': d['top'][i],
                'text': d['text'][i]
            }
            ocr_results.append(ocr_result)
    return ocr_results


if __name__ == '__main__':
    app.run(debug=True)
