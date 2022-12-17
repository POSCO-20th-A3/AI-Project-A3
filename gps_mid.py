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


def find_angle(x, y):  # 크면 왼쪽, 작으면 오른쪽
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


pwm = 1
time.sleep(2)
ard.write([pwm])  # start and initialize
start_point = disq.popleft()  # 시작 좌표 빼고 시작
start_angle = angleq.popleft()  # 0빼고
target = target_position()  # first goal
line_angle = angleq.popleft()
print(start_point, start_angle)
print(target, line_angle)
turn_left = 0
turn_right = 0
while disq:  # queue 가 텅 빌 때까지
    line = sio.readline()

    if(line[0:6] == '$GPRMC'):
        test = line.split(',')
        if test[2] == 'A':
            gps = convert_gps(test[3], test[5])  # 현재 gps 좌표(실수형)
            angle = find_angle(gps, target)
            print(gps)
            # if line_angle < angle:
            #     print(line_angle, angle)
            #     ang = 4
            #     turn_left += 1
            #     ard.write([ang])

            # elif line_angle > angle:
            #     print(line_angle, angle)
            #     ang = 5
            #     turn_right += 1
            #     ard.write([ang])

        if gps_dist(gps, target) <= boundary:
            pwm = 2
            ard.write([pwm])
            print('stop', gps_dist(gps, target))
            time.sleep(5)
            target = target_position()
            pwm = 1
            ard.write([pwm])
