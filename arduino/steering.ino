#include "Wire.h"

#include "I2Cdev.h"
#include "MPU9250.h"

float current_lat = 36.0096155555; // 현재 위도
float current_lon = 129.3225755555; // 현재 경도
float target_lat = 36.0106455555; // 목표 위도
float target_lon = 129.3229755555; // 목표 경도

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU9250 accelgyro;
I2Cdev   I2C_M;

void getAccel_Data(void);
void getGyro_Data(void);
void getCompass_Data(void);
void getCompassDate_calibrated ();

uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;


volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

float distance_lat_deg = 111.644;  // 위도 1도의 거리
//float distance_lon_deg = 88.0; // 경도 1도의 거리
float distance_lon_deg = 81.8; // 경도 1도의 거리

float heading;
float tiltheading;

float Axyz[3];
float Gxyz[3];
float Mxyz[3];

#define sample_num_mdate  5000

volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

float temperature;
float pressure;
float atm;
float altitude;

void setup()
{
    Wire.begin();
    Serial.begin(38400);                        // 통신속도 38400 bps

    Serial.println("Initializing I2C devices...");
    accelgyro.initialize();

    // verify connection
    Serial.println("Testing device connections...");
    Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");
    //조향모터 연결
    pinMode(9, OUTPUT);//PWM
    pinMode(8, OUTPUT);
    pinMode(7, OUTPUT);
    //구동 모터 연결
    pinMode(6, OUTPUT);//PWM
    pinMode(4, OUTPUT);
    pinMode(2, OUTPUT);

    delay(1000);
    Serial.println("     ");
    Mxyz_init_calibrated (); // 초기 보정 실시
}

int target_angle;

void loop()
{ 
  getAccel_Data();
  getGyro_Data();
  getCompassDate_calibrated(); // compass data has been calibrated here
  getHeading();               //before we use this function we should run 'getCompassDate_calibrated()' frist, so that we can get calibrated data ,then we can get correct angle .
  
  Serial.println("calibration parameter: ");
  Serial.print(mx_centre);
  Serial.print("         ");
  Serial.println(my_centre);
  Serial.println("         ");
  Serial.println("The clockwise angle between the magnetic north and X-Axis:");
  Serial.print(heading);
  Serial.println(" ");

  int angle = get_angle(current_lat, current_lon, target_lat, target_lon);
  move_azimuth_angle(angle);
  target_angle = angle;

  delay(1000); 
}
float get_angle(float start_lat, float start_lon, float end_lat, float end_lon) // 경도 위도 두점 간의 각도 계산
{
  float deg_lat = end_lat - start_lat;
  float deg_lon = end_lon - start_lon;
  float dist_lat = deg_lat * distance_lat_deg * 1000.0;
  float dist_lon = deg_lon * distance_lon_deg * 1000.0;
  float angle = atan2(dist_lon, dist_lat) * 180.0 / PI;
  return angle;
}

float get_my_angle(void)
{//방향 계산
    heading = -(180 * atan2(Mxyz[1], Mxyz[0]) / PI);
    if (heading < 0) heading += 360;
    return heading;
}

void getHeading(void)
{//방향 계산
    heading = -(180 * atan2(Mxyz[1], Mxyz[0]) / PI);
    if (heading < 0) heading += 360;
}

void Mxyz_init_calibrated () //초기 보정 
{
    Serial.println(F("Before using 9DOF,we need to calibrate the compass frist,It will takes about 2 minutes."));
    Serial.print("  ");
    Serial.println(F("During  calibratting ,you should rotate and turn the 9DOF all the time within 2 minutes."));
    Serial.print("  ");
    Serial.println(F("If you are ready ,please sent a command data 'ready' to start sample and calibrate."));
    
    delay(10000);
    
    Serial.println("  ");
    Serial.println("ready");
    Serial.println("Sample starting......");
    Serial.println("waiting ......");

    get_calibration_Data ();
}
void get_calibration_Data ()
{   
  for (int i = 0; i < sample_num_mdate; i++)
  {//보정 값 측정을 위해 좌회전
    turn_left(255);
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
void getAccel_Data(void)
{//가속도 데이터 측정
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Axyz[0] = (double) ax / 16384;
    Axyz[1] = (double) ay / 16384;
    Axyz[2] = (double) az / 16384;
}
void getGyro_Data(void)
{//자이로 데이터 측정
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Gxyz[0] = (double) gx * 250 / 32768;
    Gxyz[1] = (double) gy * 250 / 32768;
    Gxyz[2] = (double) gz * 250 / 32768;
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
  Mxyz[0] = Mxyz[0] - mx_centre;
  Mxyz[1] = Mxyz[1] - my_centre;
  Mxyz[2] = Mxyz[2] - mz_centre;
}

#define ALLOW_DEVIATION 5
#define REPEAT_NO 10
void move_azimuth_angle(int target) // 차량을 목표 방위각으로 회전
{
  while (target > 180)
  {
    target -= 360;
  }
  while (target < -180)
  {
    target += 360;
  }
  while (1)
  {
    float sum_angle = 0;

    for ( int i = 0; i < REPEAT_NO; i++)
    { 
      getCompassDate_calibrated(); // compass data has been calibrated here
      float angle = get_my_angle();
      sum_angle = sum_angle + angle;
    }
    float current_angle = sum_angle / (float)REPEAT_NO;

    float deviation = target - current_angle;
    while ( deviation > 180 )
    {
      deviation -= 360;
    }
    while ( deviation < -180 )
    {
      deviation += 360;
    }
    if ( fabs(deviation) < ALLOW_DEVIATION )
    {
      Serial.println("OK");
      stop();
      return;
    }

    if ( deviation  > ALLOW_DEVIATION )
    {
      turn_right(100);
    }
    if ( deviation < -ALLOW_DEVIATION )
    {
      turn_left(100);
    }
  }
}

void turn_right(int pwm){//우회전
  analogWrite(9, 255);
  digitalWrite(8, HIGH);
  digitalWrite(7, LOW);
  analogWrite(6, pwm);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}

void turn_left(int pwm){//좌회전
  analogWrite(9, 255);
  digitalWrite(8, LOW);
  digitalWrite(7, HIGH);
  analogWrite(6, pwm);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}

void stop(){//정지
  analogWrite(9, 0);
  digitalWrite(8, LOW);
  digitalWrite(7, HIGH);
  analogWrite(6, 0);
  digitalWrite(4, HIGH);
  digitalWrite(2, LOW);
}

