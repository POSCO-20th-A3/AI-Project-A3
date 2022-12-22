import pyaudio
import wave
import keyboard
import os
import glob
import librosa
import numpy as np
import io
import serial
import pandas as pd
import pickle
import serial
import time
import tensorflow as tf
from tensorflow import keras
from keras import layers, datasets, backend
from keras.models import Sequential, Model, load_model
from keras.layers import Input, Dense, Activation
from keras.utils import to_categorical
from keras.preprocessing.image import ImageDataGenerator
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3

MAX_PAD_LENGTH = 130

N_COLUMNS = 130
N_ROWS = 40
N_CHANNELS1 = 1
N_CHANNELS2 = 2
N_CLASSES = 4
signal=False

def check_len(file_name):
    audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
    #mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    return (audio.shape[0]/float(sample_rate))


def check_shape(file_name):
    audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    return mfccs.shape[1]


def check_file_num(file_name):  # 파일의 녹음 순서
    result = file_name.split('.')[0]
    return int(result)


def extract_feature(file_name):
    audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    if mfccs.shape[1] <= MAX_PAD_LENGTH:
        pad_width = MAX_PAD_LENGTH - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=(
            (0, 0), (0, pad_width)), mode='constant')
    else:
        return None
    return mfccs


def get_input_files():
    os.chdir('C:/Users/user/Desktop/AI_project/code/data')

    WAVE_OUTPUT_FILENAME1 = "1.wav"
    WAVE_OUTPUT_FILENAME2 = "2.wav"

    p = pyaudio.PyAudio()

    stream1 = p.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK,
                     input_device_index=1)

    stream2 = p.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK,
                     input_device_index=2
                     )

    frames1 = []
    frames2 = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream1.read(CHUNK)
        frames1.append(data)
        data = stream2.read(CHUNK)
        frames2.append(data)

    stream1.stop_stream()
    stream1.close()
    stream2.stop_stream()
    stream2.close()
    p.terminate()

    wf1 = wave.open(WAVE_OUTPUT_FILENAME1, 'wb')
    wf1.setnchannels(CHANNELS)
    wf1.setsampwidth(p.get_sample_size(FORMAT))
    wf1.setframerate(RATE)
    wf1.writeframes(b''.join(frames1))
    wf1.close()

    wf2 = wave.open(WAVE_OUTPUT_FILENAME2, 'wb')
    wf2.setnchannels(CHANNELS)
    wf2.setsampwidth(p.get_sample_size(FORMAT))
    wf2.setframerate(RATE)
    wf2.writeframes(b''.join(frames2))
    wf2.close()


def check_scream():
    model = load_model('C:/Users/user/Desktop/AI_project/code/latest_model2.h5')
    file_names2 = os.listdir(
        'C:/Users/user/Desktop/AI_project/code/data/')  # list of file names

    shape_list = []
    len_list = []
    feature_list = []
    for i in file_names2:
        len_list.append(check_len(i))
        shape_list.append(check_shape(i))
        feature_list.append(extract_feature(i))

    test = pd.DataFrame()
    test['data'] = feature_list
    test['shape'] = shape_list
    test['len'] = len_list

    real_x = np.array(test.data.tolist())
    real_x = tf.reshape(real_x, [-1, N_ROWS, N_COLUMNS, N_CHANNELS1])

    result1 = model.predict(real_x)
    result1_ = []
    for i in result1:
        result1_.append(i.argmax())

    if 1 in result1_:
        print("비명이 감지되었습니다")
        return True
    else:
        print("비명이 감지되지 않습니다")
        return False


def create_test_data(foldername):
    # 경로 변경 필요
    file_names = os.listdir(foldername)  # list of file names
    os.chdir(foldername)

    # 이하 미수정
    len_list_left = []
    len_list_right = []
    shape_list_left = []
    shape_list_right = []
    num_list_left = []
    num_list_right = []
    file_names_left = []
    file_names_right = []
    data_mfcc_left = []
    data_mfcc_right = []

    for file_name in file_names:
        if check_file_num(file_name) % 2 == 1:
            len_list_right.append(check_len(file_name))
            shape_list_right.append(check_shape(file_name))
            num_list_right.append(check_file_num(file_name))
            file_names_right.append(file_name)
            data_mfcc_left.append(extract_feature(file_name).tolist())
        else:
            len_list_left.append(check_len(file_name))
            shape_list_left.append(check_shape(file_name))
            num_list_left.append(check_file_num(file_name))
            file_names_left.append(file_name)
            data_mfcc_right.append(extract_feature(file_name).tolist())

    dfL = pd.DataFrame()
    dfR = pd.DataFrame()

    dfL['LEN_left'] = len_list_left
    dfL['SHAPE_left'] = shape_list_left
    dfL['FILE_NUM_left'] = num_list_left
    dfL['FILE_NAMES_left'] = file_names_left
    dfL['DATA_left'] = data_mfcc_left

    dfR['LEN_right'] = len_list_right
    dfR['SHAPE_right'] = shape_list_right
    dfR['FILE_NUM_right'] = num_list_right
    dfR['FILE_NAMES_right'] = file_names_right
    dfR['DATA_right'] = data_mfcc_right

    dfL.sort_values(by=['FILE_NUM_left'], axis=0, ascending=True, inplace=True)
    dfL.reset_index(inplace=True, drop=True)

    dfR.sort_values(by=['FILE_NUM_right'], axis=0,
                    ascending=True, inplace=True)
    dfR.reset_index(inplace=True, drop=True)

    # 방향 정보 수정
    returndata = pd.concat([dfL, dfR], axis=1)

    return returndata


def check_sound_source():
    model = load_model('C:/Users/user/Desktop/AI_project/code/ssl_model.h5')
    # 방향별 데이터프레임
    df_ = create_test_data(
        foldername='C:/Users/user/Desktop/AI_project/code/data/')

    # 데이터프레임 결합
    df = pd.concat([df_[['DATA_left']], df_[['DATA_right']]], axis=1)
    df.reset_index(inplace=True, drop=True)

    # 왼쪽 녹음 파일과 오른쪽 녹음 파일로 나뉜 mfcc값을 하나의 column으로 결합
    data_total = []
    for i in range(df.shape[0]):
        data_mfcc = []
        data_mfcc.append(df.DATA_left[i])
        data_mfcc.append(df.DATA_right[i])
        data_total.append(data_mfcc)
    df.drop(['DATA_left', 'DATA_right'], axis=1, inplace=True)
    df['DATA'] = data_total

    real_x = np.array(df.DATA.tolist())
    real_x = tf.reshape(real_x, [-1, N_ROWS, N_COLUMNS, N_CHANNELS2])

    result2 = model.predict(real_x)
    if result2[0][0] > result2[0][1]:
        return 'LEFT'
    else:
        return 'RIGHT'


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


# main code
physical_devices = tf.config.list_physical_devices('GPU')
try:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
    # Invalid device or cannot modify virtual devices once initialized.
    pass




ard = serial.Serial('COM5', 9600)
ser = serial.Serial('COM7', 9600, timeout=0.5)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))  # to read Serial
pwm = 1
time.sleep(2)
ard.write([pwm])
time.sleep(5)
print('start recording')
get_input_files()
scream = check_scream()
if scream == True:
    pwm = 3
    time.sleep(2)
    ard.write([pwm])
    direction = check_sound_source()
    print(direction)
    line = sio.readline()
    if (line[0:6] == '$GPRMC'):
        test = line.split(',')
        gps = convert_gps(test[3], test[5])  # 현재 gps 좌표(실수형)
        print(gps)
pwm=1
time.sleep(2)
ard.write([pwm])