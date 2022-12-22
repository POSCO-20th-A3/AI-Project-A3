#include <SoftwareSerial.h>
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU9250.h"
// 임시 초기화 
MPU9250 accelgyro;
I2Cdev   I2C_M;

void getCompass_Data(void);
void getCompassDate_calibrated ();
//지자계센서 raw 데이터 
int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;

//보정을 위한 초기화 값들 
volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;


static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

float heading;   //올려주는 반환값 현재 방향 
float Mxyz[3];
#define sample_num_mdate  5000  //get_calibration_data함수에 사용 


void setup() {
  Wire.begin();
  Serial.begin(9600);
  //조향 모터
  pinMode(9, OUTPUT);//PWM
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  //구동 모터
  pinMode(6, OUTPUT);//PWM
  pinMode(4, OUTPUT);
  pinMode(2, OUTPUT);

  delay(10000);
  //Mxyz_init_calibrated(); // 초기 보정 실시 한바퀴 뺑글
  //delay(5000); 
}

void loop() {
  if (Serial.available()) {
    int in_data;
    float angle;
    getCompassDate_calibrated(); //지자계 센서 값 측정 
    angle = get_my_angle();
    in_data = Serial.read();
    Serial.println(angle);
    
    if(in_data == 1){ //직진
      Go_straight();
    } 
    else if (in_data == 2){//정지
      stop();
    }
    else if (in_data == 4) {//좌회전
      turn_left();
    }
    else if (in_data == 5) {//우회전
    turn_right();
    }
  }
}
float get_my_angle(void)
{//방향 계산
    heading = -(180 * atan2(Mxyz[1], Mxyz[0]) / PI);
    if (heading < 0) heading += 360;
    return heading;
}

void Go_straight(){ //직진
  analogWrite(9, 0);
  digitalWrite(8, HIGH);
  digitalWrite(7, LOW);
  analogWrite(6, 100);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}
void stop(){ //정지
  analogWrite(9, 0);
  digitalWrite(8, HIGH);
  digitalWrite(7, LOW);
  analogWrite(6, 0);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}
void turn_left(){  //좌회전
  analogWrite(9, 100);
  digitalWrite(8, LOW);
  digitalWrite(7, HIGH);
  analogWrite(6, 80);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}
void turn_right(){ //우회전 
  analogWrite(9, 100);
  digitalWrite(8, HIGH);
  digitalWrite(7, LOW);
  analogWrite(6, 80);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}

void Mxyz_init_calibrated () //초기 보정 
{
    get_calibration_Data ();
}

void get_calibration_Data ()
{   
  for (int i = 0; i < sample_num_mdate; i++)
  {//보정 값 측정을 위해 좌회전
    turn_left();
    getCompass_Data();//지자계 측정치 불러오기
    if ( Mxyz[0] > mx_max )
    {
      mx_max = Mxyz[0];
    }
    if ( Mxyz[0] < mx_min )
    {
      mx_min = Mxyz[0];
    }
    if ( Mxyz[1] > my_max )
    {
      my_max = Mxyz[1];
    }
    if ( Mxyz[1] < my_min )
    {
      my_min = Mxyz[1];
    }
  }
  //보정이 끝나면 정지
  stop();

  mx_centre = (mx_max + mx_min) / 2;
  my_centre = (my_max + my_min) / 2;
  mz_centre = (mz_max + mz_min) / 2;
}
void getCompass_Data(void)
{//지자계 데이터 측정
  accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
  Mxyz[0] = (double) mx * 1200 / 4096;
  Mxyz[1] = (double) my * 1200 / 4096;
  Mxyz[2] = (double) mz * 1200 / 4096;
}

void getCompassDate_calibrated ()
{//방향 보정       
  getCompass_Data();
  mx_centre=1;
  my_centre=-9;
  Mxyz[0] = Mxyz[0] - mx_centre;
  Mxyz[1] = Mxyz[1] - my_centre;
  Mxyz[2] = Mxyz[2] - mz_centre;
}

