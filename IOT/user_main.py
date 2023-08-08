import time
import contourthermalcam as ctc
import pandas as pd
import test_servomotor as ts
import threading
import RPi.GPIO as GPIO
import pixel
from math import *
from picamera2 import Picamera2, Preview

data_array_mod=0
distance = 0
temperature1 = 0
temperature2 = 0 
flag_high_temp=0
highest_x,highest_y = 0,0
yaw_deg=0
pitch_deg=0
np_deg = 90
ny_deg = 90
flag_fire=0
flag_time_inc = 1
flag_inc = 1
temp_history = []
relay = 37

def save_camera():
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
    picam2.configure(camera_config)
    #picam2.start_preview(Preview.QTGL)
    picam2.start()
    index = 0
    while True:
        image_name = str(index) + ".jpg"
        picam2.capture_file(image_name)
        index += 1
        print('sex')
        if index == 6:
            index = 0
        time.sleep(1)   

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(16,GPIO.LOW)
GPIO.setwarnings(False)	

def handler():
    while True:
        get_data()
        inc_deg()
        check_highest_point()
        flag_print()
        time.sleep(1)
        
def flag_print():
    print(f"flag_time_inc:{flag_time_inc} ,flag_inc:{flag_inc} ,flag_high_temp:{flag_high_temp} ,flag_fire:{flag_fire}")
    # print(flag_fire ,flag_time_inc ,flag_inc ,flag_high_temp)
# 0. 센서 데이터 받아오기 (thread)
def get_data():
    try:
        csv_data = pd.read_csv("/home/pc/Desktop/thermalcam.csv",header=None)
        csv_data2 = pd.read_csv("/home/pc/Desktop/sensor_value.csv",header=None)
        arr_data_csv = csv_data[1:]
        global data_array_mod
        global distance   
        global temperature1
        data_array_mod = ctc.reshap_array(arr_data_csv)
        distance = csv_data2[0][1]
        temperature1 = csv_data2[1][1] 
    except Exception as ex:
        get_data()
    
    
# 1.기초적인 시간흐름에 따른 yaw 각도 증감 (thread)
def inc_deg():
    global yaw_deg, pitch_deg, flag_time_inc, flag_inc
    if flag_time_inc == 1:
        if flag_inc == 1:
            yaw_deg += 6
            if yaw_deg >= 360:
                flag_inc = 0
        else : 
            yaw_deg -= 6    
            if yaw_deg <= 0:
                flag_inc = 1
    y1_deg,y2_deg,p_deg = ts.assignDegree(yaw_deg, pitch_deg)
    ts.setServoPos_y1(y1_deg)
    ts.setServoPos_y2(y2_deg)
    ts.setServoPos_p(p_deg)

    
    
# 2. highest point가 최소 70도 이상인지 판단
def check_highest_point():
    global highest_x
    global highest_y
    global flag_high_temp
    global flag_fire
    global data_array_mod
    global temperature2
    highest_x, highest_y = ctc.get_highest_point(data_array_mod)
    temperature2 = data_array_mod[highest_y][highest_x]
    if data_array_mod[highest_y][highest_x]>=70:
        flag_high_temp = 1
        flag_time_inc = 0
    elif data_array_mod[highest_y][highest_x]>=150:
        flag_fire=1

    if flag_high_temp == 1:
        temp_history.append(data_array_mod[highest_y][highest_x])
        
        if len(temp_history) > 15:
            del(temp_history[0])
        if(data_array_mod[highest_y][highest_x])>=150:
            flag_fire=1

    
    
# 3. 해당 위치로 중심을 이동 (만약 중간이 아니라면 위의 과정 반복)
def move_center():
    global highest_x
    global highest_y 
    while (highest_x != 11) or (highest_y != 15): #수정 바람
        highest_x, highest_y = ctc.get_highest_point(data_array_mod)
        dy,dp = ts.getDegree(highest_x, highest_y) #옮길 위치
        yaw_deg = (yaw_deg+dy)%360
        pitch_deg += dp
        time.sleep(3)
    
# 4. 화재인지 판단 (아닌경우 각도를 틀어버림 최고온점이 화면 밖으로 가도록)
def judge_fire():
    global highest_x
    global highest_y 
    threshold = 2
    threshold_deadline=10

    threshold_sum = 0
    threshold_count=0

    is_red = pixel.check_red(highest_x, highest_y, 100)
    check_len =(3-is_red)*5
    while len(temp_history) <= check_len and flag_fire == 0 :
        time.sleep(0.5)
    temp_arr = temp_history[:]
    for i in range (len(temp_arr)-check_len,len(temp_arr)-1):
        if temp_arr[i+1]-temp_arr[i]>=threshold:
            threshold_count+=1
            threshold_sum+=temp_arr[i+1]-temp_arr[i]
    if threshold_sum >=threshold_deadline and temp_arr[len(temp_arr)-1]-temp_arr[len(temp_arr)-check_len]>=20:
        flag_fire = 1

def non_fire() : #화재아닌경우 시퀸스
  global flag_inc, y1_deg, y2_deg, p_deg
  pitch_center = (90-55/2)
  yaw_12pixel_deg = 18
  y_deg = y1_deg + y2_deg
  if flag_inc == 1 :
    y_deg += yaw_12pixel_deg 
    if y_deg > 180 :
      y1_deg = 180
      y2_deg = y_deg - 180
    elif y_deg > 360 :
      y1_deg = y_deg % 360
      y2_deg = 0
    else :
      y1_deg = y_deg
      y2_deg = 0

  else :
    y_deg -= yaw_12pixel_deg 
    if y_deg <=180 :
      y1_deg = y_deg
      y2_deg = 0
    elif y_deg < 0 :
      y1_deg = 180
      y2_deg = (y_deg % 360) - 180
    else :
      y1_deg = 180
      y2_deg = y_deg - 180
    p_deg = pitch_center

 

# 5. 화재이면 거리 측정후 노즐 각도 조절하여 일정시간 동안 물 분사
def nozzle_deg_distance(p_deg, distance,velocity):
    global np_deg
    val_old = 0
    for i in range (p_deg, 0, -1):
        rad2 = radians(i)
        rad1 = radians(p_deg)
        val_new = tan(rad2)-tan(rad1)+4.9*distance/pow((velocity*cos(rad2), 2))
        if (val_old*val_new < 0) or (val_new ==0):
            break
        val_old = val_new
    np_deg = i
    ts.setServoPos_n(i)
    
    

def spray():#물뿌릴때 돌리는 함수
    global np_deg , ny_deg
    for i in range (-10,10,1) :
        for j in range (-10,10,1) : 
            ts.setServoPos_np(np_deg + i/10)
            ts.setServoPos_ny(ny_deg + j/10)
    #

    

def extinguish(ext_time):
    nozzle_deg_distance()
    GPIO.output(relay,GPIO.HIGH)   
    spray()
    GPIO.output(relay,GPIO.LOW)

# 6. 처음으로
    flag_fire=0     #화재종료
    high_temp=0     #highest포인트 재탐색시작
    flag_time_inc=1 #시간에 따른 각도증가 

def activate():
    t = threading.Thread(target=handler)
    t2= threading.Thread(target = save_camera)
    t.start()
    t2.start()
    t.join()
    t2.join()
    while True:
        if flag_high_temp == 1:
            move_center()
            judge_fire()
            if flag_fire == 1:
                extinguish(ext_time)
                while temperature2>=70:
                    move_center()
                    extinguish(ext_time)
            else:
                non_fire()
                flag_high_temp = 0
                flag_time_inc = 1