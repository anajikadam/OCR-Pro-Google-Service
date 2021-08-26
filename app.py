import os
import time
from flask import Flask, redirect, url_for, flash, request, render_template, session, jsonify
from werkzeug.utils import secure_filename
# from gevent.pywsgi import WSGIServer

from app1 import Drive_OCR

# Define a flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        t = time.localtime()
        timestamp = time.strftime('%b-%d-%Y_%H%M', t)
        fileName = timestamp + '_' + f.filename
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(  basepath, 'uploads', secure_filename(fileName) )
        f.save(file_path)
        ob = Drive_OCR(file_path)
        text = ob.main()
        session['text'] = text
        session['path'] = fileName
        return {'ImgPath':file_path, 'Text':text}
    return None

@app.route('/saveText', methods=['GET', 'POST'])
def saveText():
    text = session.get('text', None)
    path = session.get('path', None)
    fileName = path.split('.')[0]+'.txt'
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(  basepath, 'textFiles', secure_filename(fileName) )
    with open(file_path, 'w', encoding="utf-8") as in_file:
        in_file.write(str(text))
    return render_template('index1.html', data=text, file_path=file_path, text=text)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# http://127.0.0.1:5000/api/getText
@app.route('/api/getText', methods=['POST'])
def getText():
        # Catch the image file from a POST request
    if 'file' not in request.files:
        return "Please try again. rename KEY name is file"
    if request.method == 'POST':
        f = request.files['file']
        fname = f.filename
    if f and allowed_file(f.filename):
        t = time.localtime()
        timestamp = time.strftime('%b-%d-%Y_%H%M', t)
        fileName = timestamp + '_' + f.filename
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(  basepath, 'uploads', secure_filename(fileName) )
        f.save(file_path)
        ob = Drive_OCR(file_path)
        text = ob.main()
        fileName1 = fileName.split('.')[0]+'.txt'
        file_path1 = os.path.join(  basepath, 'textFiles', secure_filename(fileName1) )
        with open(file_path1, 'w', encoding="utf-8") as in_file:
            in_file.write(str(text))
    else:
        print("Please Select PDF file Only")
        return "Please Select PDF file Only"

    result = {
                "Number": 1011,
                "File Name": fname,
                "File Path": file_path,
                "Text File Path":file_path1,
                "Text": str(text)
            }
    return jsonify(result)

# http://127.0.0.1:5000/api/ocrForImageDir
@app.route('/api/ocrForImageDir', methods=['GET'])
def ocrForImageDir():
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(  basepath, 'Images')
    filesList = os.listdir(file_path)
    filesList = [i for i in filesList if i.split('.')[-1].lower() in ALLOWED_EXTENSIONS]
    files = []
    filePath = []
    textL = []
    for file in filesList:
        f = file_path+'\\'+file
        print(f)
        ob = Drive_OCR(f)
        text = ob.main()
        fileName1 = file_path+'\\'+file.split('.')[0]+'.txt'
        with open(fileName1, 'w', encoding="utf-8") as in_file:
            in_file.write(str(text))
        files.append(f)
        textL.append(text)
        filePath.append(fileName1)
    data = []
    for i in range(len(files)):
        d = {"id":i,"Details":{"File Name": files[i],
                                "Text File Name":filePath[i],
                                "Text":textL[i]}}
        data.append(d)

    result = {
                "Number": 1012,
                "OCR Details":data
            }
    return jsonify(result)

# http://127.0.0.1:5000/api/OCR_dir/<directory_name>
@app.route('/api/OCR_dir/<dir>', methods=['GET'])
def OCR_dir(dir = "None"):
    directory = dir
    print(directory)
    basepath = os.path.dirname(__file__)
    if os.path.isdir(directory):
        file_path = os.path.join(  basepath, directory)
        filesList = os.listdir(file_path)
        filesList = [i for i in filesList if i.split('.')[-1].lower() in ALLOWED_EXTENSIONS]
        files = []
        filePath = []
        textL = []
        for file in filesList:
            f = file_path+'\\'+file
            print(f)
            ob = Drive_OCR(f)
            text = ob.main()
            fileName1 = file_path+'\\'+file.split('.')[0]+'.txt'
            with open(fileName1, 'w', encoding="utf-8") as in_file:
                in_file.write(str(text))
            files.append(f)
            textL.append(text)
            filePath.append(fileName1)
        data = []
        for i in range(len(files)):
            d = {"id":i,"Details":{"File Name": files[i],
                                    "Text File Name":filePath[i],
                                    "Text":textL[i]}}
            data.append(d)
        result = {
                    "Number": 1013,
                    "OCR Details":data
                }
        return jsonify(result)

    result = {
                "Number": 1013,
                "Details":"Directory Not Present"
            }
    return jsonify(result)
    

if __name__ == '__main__':
    app.secret_key = "Drmhze6EPcv0fN_81Bj-nA"
    app.config['JSON_SORT_KEYS'] = False
    app.run(debug=True)
