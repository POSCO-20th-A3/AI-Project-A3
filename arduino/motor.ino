void setup() {
  Serial.begin(9600);
  //조향 모터
  pinMode(9, OUTPUT);//PWM
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  //구동 모터
  pinMode(6, OUTPUT);//PWM
  pinMode(4, OUTPUT);
  pinMode(2, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char in_data;
    in_data = Serial.read();
    Serial.println(in_data);
    if (in_data == '1') { //직진
      analogWrite(9, 80);
      digitalWrite(8, LOW);
      digitalWrite(7, HIGH);
      delay(500);
      analogWrite(9, 0);
      digitalWrite(8, LOW);
      digitalWrite(7, HIGH);
      analogWrite(6, 150);
      digitalWrite(4, HIGH);
      digitalWrite(2, LOW);

    } else if (in_data == '2') {//정지
      analogWrite(9, 0);
      digitalWrite(8, HIGH);
      digitalWrite(7, LOW);
      analogWrite(6, 0);
      digitalWrite(4, HIGH);
      digitalWrite(2, LOW);

    } else if (in_data == '3') {//후진
      analogWrite(9, 0);
      digitalWrite(8, LOW);
      digitalWrite(7, HIGH);
      analogWrite(6, 150);
      digitalWrite(4, LOW);
      digitalWrite(2, HIGH);
    }else if (in_data == '4') {//우회전
      analogWrite(9, 255);
      digitalWrite(8, HIGH);
      digitalWrite(7, LOW);
      analogWrite(6, 150);
      digitalWrite(4, HIGH);
      digitalWrite(2, LOW);
    }else if (in_data == '5') {//좌회전
      analogWrite(9, 255);
      digitalWrite(8, LOW);
      digitalWrite(7, HIGH);
      analogWrite(6, 150);
      digitalWrite(4, HIGH);
      digitalWrite(2, LOW);
    }
  }
}