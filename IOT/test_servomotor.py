import RPi.GPIO as GPIO
import time

servoPin_y1 = 36
servoPin_y2 = 38
servoPin_p = 40
servoPin_np = 37
servoPin_ny = 35

SERVO_MAX_DUTY_y1    = 12.3   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY_y1    = 2.4    # 서보의 최소(0도) 위치의 주기
SERVO_MAX_DUTY_y2    = 12.3   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY_y2    = 2.4    # 서보의 최소(0도) 위치의 주기
SERVO_MAX_DUTY_p    = 11.9   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY_p    = 2.4    # 서보의 최소(0도) 위치의 주기
SERVO_MAX_DUTY_np    = 12   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY_np    = 2.3    # 서보의 최소(0도) 위치의 주기
SERVO_MAX_DUTY_ny    = 12   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY_ny    = 2.3    # 서보의 최소(0도) 위치의 주기



#GPIO.setmode(GPIO.BOARD)        # GPIO 설정
GPIO.setwarnings(False)	
GPIO.setup(servoPin_y1, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(servoPin_y2, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(servoPin_p, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(servoPin_np, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(servoPin_ny, GPIO.OUT)  # 서보핀 출력으로 설정

servo_y1 = GPIO.PWM(servoPin_y1, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo_y1.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.
servo_y2 = GPIO.PWM(servoPin_y2, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo_y2.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.
servo_p = GPIO.PWM(servoPin_p, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo_p.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.
servo_np = GPIO.PWM(servoPin_np, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo_np.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.
servo_ny = GPIO.PWM(servoPin_ny, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo_ny.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.

def setServoPos_y1(degree) :
  if degree > 180 :
    degree = 180
  if degree < 0 :
    degree = 0
  duty = SERVO_MIN_DUTY_y1+(degree*(SERVO_MAX_DUTY_y1-SERVO_MIN_DUTY_y1)/180.0)
  servo_y1.ChangeDutyCycle(duty)

def setServoPos_y2(degree) :
  if degree > 180 :
    degree = 180
  if degree < 0 :
    degree = 0
  duty = SERVO_MIN_DUTY_y2+(degree*(SERVO_MAX_DUTY_y2-SERVO_MIN_DUTY_y2)/180.0)
  servo_y2.ChangeDutyCycle(duty)

def setServoPos_p(degree) :
  if degree > 90 :
    degree = 90
  if degree < 0 :
    degree = 0
  duty = SERVO_MIN_DUTY_p+(degree*(SERVO_MAX_DUTY_p-SERVO_MIN_DUTY_p)/180.0)
  servo_p.ChangeDutyCycle(duty)

def setServoPos_np(degree) :
  if degree > 180 :
    degree = 180
  if degree < 0 :
    degree = 0
  duty = SERVO_MIN_DUTY_np+(degree*(SERVO_MAX_DUTY_np-SERVO_MIN_DUTY_np)/180.0)
  servo_np.ChangeDutyCycle(duty)

def setServoPos_ny(degree) :
  if degree > 180 :
    degree = 180
  if degree < 0 :
    degree = 0
  duty = SERVO_MIN_DUTY_ny+(degree*(SERVO_MAX_DUTY_ny-SERVO_MIN_DUTY_ny)/180.0)
  servo_ny.ChangeDutyCycle(duty)

def getDegree(x,y) :
  x_dfr = x-11
  y_dfr = y-15
  x_1pixel = 1.45833333
  y_1pixel = 1.71875
  dyaw_deg = x_dfr * x_1pixel
  dpitch_deg = y_dfr * y_1pixel
  return dyaw_deg, dpitch_deg


def assignDegree(yaw_deg, pitch_deg) :
  if yaw_deg >360 : #yaw 범위를 0º~360º로 제한
    yaw_deg = 360
  if yaw_deg < 0 :
    yaw_deg = 0

  if yaw_deg <= 180 : #yaw값에 따라 모터1, 모터2의 각도로 배정
    degree_y1 = yaw_deg
    degree_y2 = 0
  if yaw_deg > 180 :
    degree_y1 = 180
    degree_y2 = yaw_deg - 180

  if pitch_deg > 90 : #pitch 범위를 0º~90º로 제한
    pitch_deg = 90
  if pitch_deg <0 :
    pitch_deg = 0
  degree_p = pitch_deg #pitch값을 모터3의 각도로 배정
  
  return degree_y1, degree_y2, degree_p