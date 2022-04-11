import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

def faceEncodings(images):
    """Returns the Face Ecnodings of the images passed to this function. Face Encoding of images in /images folder.

    Args:
        images (numpy.ndarray): An array of numpy.ndarray images from /images folder

    Returns:
        list : Returns a list of arrays of the Face Ecnodings of the images passed to this function
    """
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# def deleteRow(file,lines,name):
#     for line in lines:
#         entry = line.splite(',')
#         if entry[0] != name:
#             file.write(line)

def putAttendance(name):
    time_now = datetime.now()
    tStr = time_now.strftime('%H:%M:%S')
    Hour = time_now.strftime('%H%M')
    dStr = time_now.strftime('%d-%m-%Y')
    csvFile = 'Attendance-'+Hour+'-'+dStr+'.csv'
    with open(csvFile, 'w+') as f:
        dataList = f.readlines()
        nameList = []
        attendCount = []
        for line in dataList:
            entry = line.split(',')
            nameList.append(entry[0])
            attendCount.append(entry[-1])
            
        if name not in nameList:
            f.writelines(f'{name},{tStr},{dStr},1\n')
        # else:
        #     deleteRow(f,dataList,name)
        #     for line in dataList:
        #         entry = line.split(',')
        #         f.writelines(f'{name},{tStr},{dStr},{++(entry[-1])}\n')
            
            

path = 'images' #The path where the images are stored.
images = []
personName = []
name = ''

#Listing the directory of the images stored folder
listDIR = os.listdir(path)
print(listDIR)


# Iterating through the list of images, reading them, and storing them in a list images, 
# then splitting the text and storing them in personName
for current_img in listDIR:
    current_IMG = cv2.imread(f'{path}/{current_img}')
    images.append(current_IMG)
    personName.append(os.path.splitext(current_img)[0])
print(personName)

# print(faceEncodings(images))

encodeList = faceEncodings(images)
print("All Encodings complete!")

cam = cv2.VideoCapture(0) # '0' for internal camera, '1' for external camera
cv2.namedWindow("Camera")

while True:
    ret, frame = cam.read()
    faces = cv2.resize(frame, (0,0), None, 0.5, 0.5) # 0.25 resizes to 1/4 of the original resolution
    faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)
    if not ret:
        print("Error in grabbing frame")
        break
    faceNewFrame = face_recognition.face_locations(faces)
    encodeNewFrame = face_recognition.face_encodings(faces,faceNewFrame) #faces and faceNewFrame are used if more than one image lies in the frame
    name = ''
    for encodeFace, faceLocation in zip(encodeNewFrame, faceNewFrame):
        matches = face_recognition.compare_faces(encodeList, encodeFace)
        faceDistance = face_recognition.face_distance(encodeList, encodeFace)
        
        matchIndex = np.argmin(faceDistance) #np.argmin give the index of the lowest no. in the list
        # print(matches)
        # print(matchIndex)
        
        # The matchIndex is used to determine the person from personName list. matches[matchIndex] will be true only for the person  matched
        if matches[matchIndex]:
            name = personName[matchIndex]
            # print(name) # Print the name of the person matche in the terminal.
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1*2, x2*2, y2*2, x1*2 # Multiply with the no. 1/resize which is used in camera resizing
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.rectangle(frame, (x1,y2-((y2-y1)//10)), (x2,y2), (0,255,0), cv2.FILLED)
            scale = (y2-y1)/300
            print(faceDistance[matchIndex])
            # print(scale)
            cv2.putText(frame, name, (x1+6, y2-2), cv2.FONT_HERSHEY_COMPLEX, scale, (0,0,255),1)
            
        else:
            name = "unknown".upper()
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1*2, x2*2, y2*2, x1*2 # Multiply with the no. 1/resize which is used in camera resizing
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.rectangle(frame, (x1,y2-((y2-y1)//10)), (x2,y2), (0,255,0), cv2.FILLED)
            scale = (y2-y1)/300
            print(faceDistance[matchIndex])
            # print(scale)
            cv2.putText(frame, name, (x1+6, y2-2), cv2.FONT_HERSHEY_COMPLEX, scale, (0,0,255),1)
        
    cv2.imshow("Camera",frame)
    k = cv2.waitKey(10)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    if k%256 == 32:
        # Spacebar pressed
        print("Spacebar hit, saving attendace...")
        print("New Person Please")
        putAttendance(name)
    
# Releasing camera resource and deleting window
cam.release()
cv2.destroyAllWindows()