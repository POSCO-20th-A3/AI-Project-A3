import cv2
import pandas as pd
from matplotlib import pyplot as plt
from deepface import DeepFace
from deepface.commons import functions, realtime, distance as dst
import time
import copy
import os

models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]
metrics = ["cosine", "euclidean", "euclidean_l2"]
detector_backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']

save_path='/home/piai/python/project/face/save_img/'
file_path=os.listdir('/home/piai/python/project/face/compare_img')

faceCascade = cv2.CascadeClassifier("haarcascade_frontface.xml")
cap = cv2.VideoCapture(0)
start_time=time.time()

# 기준이 되는 사진 정하기
wanted_img=cv2.imread('HH.jpg')

# 기준 되는 사람 특징 추출
Facefeature_1 = DeepFace.represent(
        img_path = wanted_img,
        enforce_detection = False,
        detector_backend = detector_backends[1],
        model_name = models[2],
        align = True,
        normalization = 'Facenet512'
    )

# 기준 되는 사람(범죄자)이 인지 아닌지 확인
def check_wanted(Facefeature_1,img):
    Facefeature_2 = DeepFace.represent(
        img_path = img,
        enforce_detection = False,
        detector_backend = detector_backends[1], 
        model_name = models[2], 
        align = True,
        normalization = 'Facenet512'
    )

    distance = dst.findCosineDistance(Facefeature_1, Facefeature_2)

    if distance <= 0.05 :
        return "same"
    else :
        return "different"

while True:
    cnt=0
    c=0
    current_time=time.time()
    ret, frame =cap.read()
    img=frame.copy()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,     # 이미지에서 얼굴 크기가 서로 다른 것을 보상해주는 값
        minNeighbors=5,    # 얼굴 사이의 최소 간격(픽셀)입니다
        minSize=(30, 30),   # 얼굴의 최소 크기입니다
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


    if current_time-start_time>1:
        for (x, y, w, h) in faces:
            face = img[y-20:y+h+20, x-20:x+w+20]
            cnt+=1
            try:
                # 웹캠으로 찍은 사진을 저장
                cv2.imwrite(f'/home/piai/python/project/face/compare_img/img_{cnt}.jpg',face)
                for f in file_path:
                    # 웹캠으로 찍은 사진 불러와서
                    img1=cv2.imread('/home/piai/python/project/face/compare_img/'+f)
                    print(f)
                    #  범죄자 인지 아닌지 확인
                    result=check_wanted(Facefeature_1,img1)
                    print(result)
                    # 범죄자 이면 다른 폴더에 이미지 웹캠 화면 저장
                    if result == 'same':
                        cv2.imwrite(save_path+f'wanted_img_{c}.jpg',img1)
                        c+=1
                    else:
                        pass
            except:
                pass

        start_time=current_time

    cv2.imshow('frame',frame)

    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break
    
cap.release()
cv2.destroyAllWindows()