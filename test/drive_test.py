import serial
import time
import pandas as pd
import collections
import math
from tqdm import tqdm
import io

ard = serial.Serial('COM4', 9600)  # 아두이노 시리얼 통신

def go():
    ang = 1  # 직진
    ard.write([ang])

def stop():
    ang = 2  # 정지
    ard.write([ang])

def left():
    ang = '5'  # 좌회전
    ard.write([ang])

def right():
    ang = '4'  # 우회전
    ard.write([ang])