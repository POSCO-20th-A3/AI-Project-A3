import serial
import time
import pandas as pd
import collections
import math
from tqdm import tqdm
from haversine import haversine
import io
ard = serial.Serial('COM6', 9600)  # 아두이노 시리얼 통신
ser = serial.Serial('COM8', 9600, timeout=1.0)  # 2초마다 GNSS 수신기 시리얼 통신
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))  # to read Serial

dist = pd.read_csv('point_angle.csv')  # first target to last target string GPS
disq = collections.deque([])
angleq = collections.deque([])
boundary = 3  # 타켓 정답 판단 기준인 경계는 3m
angle_boundary = 7
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


def find_angle(x, y):  # 크면 왼쪽, 작으면 오른쪽 - 해당 각도의 기준선은 북위 0도선
    distance_lat_deg = 111.644
    distance_lon_deg = 81.8
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


def read_direction():  # 지자계가 보내는 각도 신호를 받아오는 함수
    if ard.readable():
        code = ard.readline().decode()
        direction = float(code)
        return direction  # 지자계가 보내는 각도


pwm = 1
time.sleep(2)
ard.write([pwm])  # start and initialize
start_point = disq.popleft()  # 시작 좌표 빼고 시작
start_angle = angleq.popleft()  # 0빼고
target = target_position()  # first goal
line_angle = angleq.popleft()
print(start_point, start_angle)
print(target, line_angle)
ang = 0
while disq:  # queue 가 텅 빌 때까지
    line = sio.readline()

    if (line[0:6] == '$GPRMC'):
        test = line.split(',')
        if test[2] == 'A':
            gps = convert_gps(test[3], test[5])  # 현재 gps 좌표(실수형)
            # angle = find_angle(gps, target)  # GPS로만 측정한 현재와 목표지점까지의 각도
            direction = read_direction()  # 지자계로 측정한 현재와 목표지점까지의 각도
            print(gps, direction)
            # 지자계 각도와 기존 angle(가야하는 방향의 방위각) 의 차이가 오차범위 안에 들어오면 직진 신호

            if abs(line_angle - direction) < angle_boundary:
                print(line_angle, direction)
                if ang != 1:
                    ang = 1  # 직진
                    ard.write([ang])
                else:  # 직진 상태라면
                    ang = 1  # 아두이노로 신호는 보내지 않고 갱신만 진행

            elif line_angle - direction < angle_boundary:
                print(line_angle, direction)
                ang = 4  # 좌회전
                ard.write([ang])

            elif line_angle - direction > angle_boundary:
                print(line_angle, direction)
                ang = 5  # 우회전
                ard.write([ang])
                # 지자계 각도와 기존 angle(가야하는 방향의 방위각) 의 차이가 오차범위 안에 들어오면 직진 신호

        if gps_dist(gps, target) <= boundary:
            pwm = 2
            ard.write([pwm])
            print('stop', gps_dist(gps, target))
            time.sleep(7)
            target = target_position()
            line_angle = angleq.popleft()
            pwm = 1
            ard.write([pwm])
