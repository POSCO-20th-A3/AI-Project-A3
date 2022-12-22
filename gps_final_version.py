import serial
import time
import pandas as pd
import collections
import math
from tqdm import tqdm
from haversine import haversine
import io
from datetime import datetime
import json
ard = serial.Serial('COM6', 9600, timeout=0.5)  # 아두이노 시리얼 통신
ser = serial.Serial('COM8', 9600, timeout=0.5)  # 2초마다 GNSS 수신기 시리얼 통신
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))  # to read Serial

# first target to last target string GPS
dist = pd.read_csv('point_angle_mode.csv')
disq = collections.deque([])
angleq = collections.deque([])
boundary = 2.5  # 타켓 정답 판단 기준인 경계는 2.5
angle_boundary = 5
for i in range(len(dist)):
    x, y = dist['x_y'][i].split(',')
    ang = dist['angle'][i]
    disq.append([float(x), float(y)])
    angleq.append(ang)


def convert_gps(lat, lon):  # string 10lat, 11 lon -> float GPS tuple
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


def find_angle(x, y):
    distance_lat_deg = 109.958  # 위도 37도부근 단위 위도의 거리
    distance_lon_deg = 88.74  # 위도 37도에서 단위 경도의 거리
    lat = y[0] - x[0]
    lon = y[1] - x[1]
    dist_lat = lat * distance_lat_deg*1000.0
    dist_lon = lon * distance_lon_deg*1000.0
    angle = math.atan2(dist_lon, dist_lat)
    return round(math.degrees(angle), 1)


def target_position():  # target position queue pop
    target = disq.popleft()
    return target


def gps_dist(pos, target):  # target & current pos distance
    return haversine(pos, target, unit='m')


def read_direction():  # 지자기가 보내는 각도 신호를 받아오는 함수
    if ard.readable():
        code = ard.readline().decode()
        if code == '':
            direction = 0.01
        else:
            direction = float(code)

        return direction  # 지자계가 보내는 각도


def write_json(gps):
    data = {
        'gps': gps,
        # 'time': datetime.now().time()
    }
    with open('C:\\Users\\youmi\\OneDrive\\바탕 화면\\flask_web\\helloflask\\data.json', 'w') as f:
        json.dump(data, f)


time.sleep(5)  # start and initialize
start_point = disq.popleft()  # 시작 좌표 빼고 시작
start_angle = angleq.popleft()  # 0빼고
target = target_position()  # first goal
line_angle = angleq.popleft()
print(start_point, start_angle)
print(target, line_angle)
ang = 0
pwm = 1
time.sleep(2)
ard.write([pwm])
while disq:  # queue 가 텅 빌 때까지#
    line = sio.readline()
    if (line[0:6] == '$GPRMC'):
        test = line.split(',')
        if test[2] == 'A':
            gps = convert_gps(test[3], test[5])  # 현재 gps 좌표(실수형)
            direction = read_direction()  # 지자계로 측정한 현재와 목표지점까지의 각도
            if direction == 0.01:
                direction = line_angle
            # 지자계 각도와 기존 angle(가야하는 방향의 방위각) 의 차이가 오차범위 안에 들어오면 직진 신호
            if line_angle > 180:
                line_angle -= 360
            elif line_angle < -180:
                line_angle += 360

            deviation = line_angle - direction
            if deviation < -180:
                deviation += 360
            elif deviation > 180:
                deviation -= 360

            if abs(deviation) < angle_boundary:
                print(line_angle, direction, deviation)
                if ang != 1:
                    ang = 1  # 직진
                    ard.write([ang])
                else:  # 직진 상태라면
                    ang = 1  # 아두이노로 신호는 보내지 않고 갱신만 진행

            elif deviation < angle_boundary:
                print(line_angle, direction, deviation)
                ang = 4  # 좌회전
                ard.write([ang])

            elif deviation > angle_boundary:
                print(line_angle, direction, deviation)
                ang = 5  # 우회전
                ard.write([ang])

        if gps_dist(gps, target) <= boundary:
            pwm = 2
            ard.write([pwm])
            print('stop', gps_dist(gps, target))
            write_json(gps)
            time.sleep(7)
            target = target_position()
            line_angle = angleq.popleft()
            pwm = 1
            ard.write([pwm])


# 멈춤 싸인이 아두이노에서 올라오면 이를 인식해서 해당 자리 GPS 정보를 다른 JSON으로 전송
# 'time' : 현재 시간
# 'GPS' : 현재 GPS
#detecting / lying / scream
