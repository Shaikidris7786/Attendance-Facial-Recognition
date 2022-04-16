from flask import Flask, render_template, render_template_string, url_for, request,redirect
from datetime import datetime
import os
import cv2
import face_recognition
import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename

# from flask_sqlalchemy import SQLAlchemy

def setter(count,attendance):
    Counter = count
    Attendance = attendance

# Uploading Images 
UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'jfif'])
# Function to check if the extension is acceptable
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def Emailer():
    port = 465  # 465 For SSL, 587 for TLS
    smtp_server = "smtp.gmail.com"
    sender_email = ""  # Enter your address
    # receiver_email = "skidris7786@gmail.com"  # Enter receiver address
    password = ""
    # Use this for Simple message delivery
    # message = """\
    # Subject: Hi {name}

    # This message is sent Through Python to mark your attendance."""
    
    dataList = []
    attendedName = []
    attendedNo = []
    totalNo = []
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Attendance System Auto Mail"
    message["From"] = sender_email
    # message["To"] = receiver_email
    
    studentText = """\
Hello {name},
This message is to notify that you have attended {present} out of {total} classes today. 
    """
    
    parentText = """\
Hello Sir/Ma'am,
This message is to notify that your ward, {name} has attended {present} out of {total} classes today.
        """

    server = smtplib.SMTP_SSL(smtp_server,port)
    # server = smtplib.SMTP(smtp_server,port)
    # server.starttls()
    server.login(sender_email,password)
    print("login successful")
    data = []
    keys = ['Name','Attended','Total']
    with open('att.csv', 'r') as f:
        for row in f:
            entry = row.split(',')
            data.append(dict(zip(keys,[entry[0],entry[1],entry[-1]])))
    # print(len(data))
    with open("details.csv", "r") as csvfile:
            # print(data[i]['Name'],data[i]['Attended'])
        for name,studEmail,parentEmail in csv.reader(csvfile):
            for i in range(0, len(data)):
                if data[i]['Name'] == name:
                    total = data[i]['Total'].replace('\n',' ')
                    present = data[i]['Attended']
                    # print(present,'/',total, email)
                    
                    # Student Mail
                    message["To"] = studEmail
                    message.attach(MIMEText(studentText,"plain"))
                    server.sendmail(
                        sender_email,
                        studEmail,
                        message.as_string().format(name=name,present = present,total = total)
                    )
                    
                    # Parent Mail
                    message["To"] = parentEmail
                    message.attach(MIMEText(parentText,"plain"))
                    server.sendmail(
                        sender_email,
                        parentEmail,
                        message.as_string().format(name=name,present = present,total = total)
                    )
                    
                    
    print("Mails Sent Successfully!!")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form.get('Register'):
            return redirect(url_for('register'))
        elif request.form.get('Recognise'):
            return redirect(url_for('recognise'))
        elif request.form.get('Attendance'):
            return redirect(url_for('attendance'))
        elif request.form.get('Send Email'):
            Emailer()
            return redirect(url_for('mailSent'))
    else:    
        return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['Name']
        stud_email = request.form['Student-Email']
        parent_email = request.form['Parent-Email']
        image = request.files['Image']
        var = image.filename.split(".")
        image.filename = name + '.' + var[-1]
        print(image.filename)
        with open('details.csv', 'r+') as det:
            dataList = det.readlines()
            nameList = []
            for line in dataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))        
                det.writelines(f'{name},{stud_email},{parent_email}\n')
                return redirect(url_for('success',Name = name, Student_Email = stud_email,Parent_Email = parent_email))
            else:
                return redirect(url_for('failure',Name = name))
    else:
        return render_template('register.html')
    
@app.route('/recognise', methods=['POST', 'GET'])
def recognise():
    if request.method == 'POST':
        if request.form.get('Start Camera'):
            exec(open("faceCapture.py").read())
            return redirect(url_for('attended'))
    else:
        return render_template('recognise.html')

@app.route('/attendance')
def attendance():
    Attendance = {}
    with open('details.csv','r') as det:
        dataList = det.readlines()
        nameList = []
        for line in dataList:
            entry = line.split(',')
            nameList.append(entry[0])
            Attendance = dict.fromkeys(nameList,0)
    Counter = 0
    for path, currentDirectory, files in os.walk(os.getcwd()):
        for file in files:
            if file.startswith("Attendance"):
                with open(file,'r') as att:
                    Counter = Counter + 1
                    dataList1 = att.readlines()
                    nameList1 = []
                    for line in dataList1:
                        entry = line.split(',')
                        nameList1.append(entry[0])
                        for name in nameList1:
                            Attendance[name] = Attendance[name]+1
    # print(Attendance)
    with open('att.csv', 'w') as att:
        att.truncate()
        for i in Attendance:
            name = i
            attended = Attendance[i]
            total = Counter
            setter(Counter,Attendance)
            att.writelines(f'{name},{attended},{total}\n')
    keys = ['name', 'attended','total']
    data = []
    with open('att.csv', 'r') as f:
        for row in f:
            entry = row.split(',')
            data.append(dict(zip(keys,[entry[0],entry[1],entry[-1]])))
    
    return render_template('attendance.html',data = data)

@app.route('/success')
def success():
    Name = request.args.get('Name',None)
    studEmail = request.args.get('Student_Email',None)
    parentEmail = request.args.get('Parent_Email',None)
    return render_template('success.html',Name=Name,StudentEmail=studEmail,ParentEmail=parentEmail)

@app.route('/failure')
def failure():
    Name = request.args.get('Name',None)
    return render_template('failure.html',Name=Name)

@app.route('/attended')
def attended():
    return render_template('attended.html')

@app.route('/mailSent')
def mailSent():
    return render_template('mailSent.html')

if __name__ == '__main__':
    app.run(debug=True)