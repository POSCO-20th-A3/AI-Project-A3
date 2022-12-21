import torch
import cv2
import numpy as np
import pandas as pd
import drive_test as dt
import night_vision as nv
#import checking_gps as cg
import io
import serial

ser = serial.Serial('COM7', 9600, timeout=0.5)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))  # to read Serial


def convert_gps(lat, lon):
    x1 = float(lat)
    x2 = float(lon)
    tmp1 = x1/100
    tmp2 = x2/100
    deg1 = tmp1//1
    deg2 = tmp2//1
    angle1 = (tmp1 % 1)/60*100
    angle2 = (tmp2 % 1)/60*100
    x = deg1+angle1
    y = deg2+angle2
    return (x, y)


def lyingDrive():
    model = torch.hub.load('yolov5', 'custom', path='./yolov5/lying_1216_l.pt', source='local') # or yolov5m, yolov5l, yolov5x, custom

    pred_color = {'lying' : (0,0,255), #Red
                'sit' : (0,255,0), #Blue
                'standing' : (0,255,0) #Green
                }

    cap=cv2.VideoCapture(1)
    print('ok')
    signal='go'
    while(True):

        
        line = sio.readline()
        if (line[0:6] == '$GPRMC'):
            test = line.split(',')


        ret, frame = cap.read()
        if not ret:
            break
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = nv.up(img)
        results = model(img)
        df = results.pandas().xyxy[0]
        obj_list = []
        for i in range(len(df)) :
            obj_xmin = int(df['xmin'][i])
            obj_ymin = int(df['ymin'][i])
            obj_xmax = int(df['xmax'][i])
            obj_ymax = int(df['ymax'][i])
            obj_confi = df['confidence'][i]
            obj_class = df['class'][i]
            obj_name = df['name'][i]
            obj_dict = {
                        'class' : obj_name, 
                        'confidence' : obj_confi, 
                        'bbox' : [obj_xmin,obj_ymin,obj_xmax,obj_ymax]
            }
            obj_list.append(obj_dict)
        for obj_dict in obj_list :
            class_name = obj_dict['class']
            confidence = "%.2f"%(obj_dict['confidence'])
            text_x = obj_dict['bbox'][0] + 10 #xmin + 10
            text_y = obj_dict['bbox'][1] + 20 #ymin + 10
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            if obj_dict['class'] == 'lying':
                cv2.putText(frame, class_name + ':' + confidence, (text_x, text_y), font, 0.7, thickness=2, color=pred_color[obj_dict['class']])
                cv2.rectangle(frame, (obj_dict['bbox'][0], obj_dict['bbox'][1]), (obj_dict['bbox'][2], obj_dict['bbox'][3]), color=pred_color[obj_dict['class']], thickness=2)
                signal='stop'
                gps = convert_gps(test[3], test[5])  # 현재 gps 좌표(실수형)
                print(gps)

        print(signal)
        frame = cv2.resize(frame, (640 ,640))
        cv2.imshow('lying',frame) 
        k=cv2.waitKey(30)
        if k == ord('q'):
            break
        
        if len(df) == 0:
            dt.go()
        else:
            if signal=='stop':
                dt.stop()
            else:
                dt.go()
        signal='go'
    cap.release()
    cv2.destroyAllWindows()
    dt.stop()

if __name__ == "__main__":
    lyingDrive()