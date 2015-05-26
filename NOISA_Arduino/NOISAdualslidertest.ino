#include "CapacitiveSensor.h"

int enablePin = 3;
int in1Pin = 2;
int in2Pin = 4;

int enablePin2 = 6;
int in1Pin2 = 5;
int in2Pin2 = 7;

boolean manual = true;

CapacitiveSensor   capsen = CapacitiveSensor(8,9);
CapacitiveSensor   capsen2 = CapacitiveSensor(8,10);
const int samples = 30;


boolean reverse = false;
boolean updir = false;
boolean reverse2 = false;
int target = 512;
int target2 = 512;
boolean motorstop = true;
boolean motorstop2 = true;
int precision = 50;
int manual_precision = 10;
long manualtime;
int stopStrength = 90;
int downStrength = 255;
int maxMotor = 700;
int minMotor = 350;

void setup()
{
  pinMode(in1Pin, OUTPUT);
  pinMode(in2Pin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  setPwmFrequency(enablePin, 1);
  pinMode(in1Pin2, OUTPUT);
  pinMode(in2Pin2,  OUTPUT);
  pinMode(enablePin2, OUTPUT);
  setPwmFrequency(enablePin2, 1);
  Serial.begin(115200);
  
  setMotor(updir, reverse);
  setMotor2(updir, reverse);
  
  manualtime = millis();
}

void loop()
{
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'A') {
      target = Serial.parseInt(); //min(maxMotor, max(minMotor, Serial.parseInt()));
      Serial.println(target);
    }
    if (c == 'B') {
      target2 = Serial.parseInt(); //min(maxMotor, max(minMotor, Serial.parseInt()));
      Serial.println(target2);
    }
    else if(c == 'S') {
      stopStrength = Serial.parseInt();
    }
    else if(c == 'D') {
      downStrength = Serial.parseInt();
    }
    else if(c == 'P') {
      precision = Serial.parseInt();
    }
    else if(c == 'M') {
      int ismanual = Serial.parseInt();
      if(ismanual == 0) {
        manual = false;
      }
      else {
        manual = true;
        setMotor(0, updir);
        setMotor2(0, updir);
      }
    }
  }
  
  
  unsigned long read_sense1 = capsen.capacitiveSensorAsync(samples);
  unsigned long read_sense2 = capsen2.capacitiveSensorAsync(samples);
  if(read_sense1 != -1 || read_sense2 != -1) {
      Serial.print("C\t");
      if(read_sense1 != -1) {
        Serial.print(read_sense1);
      }
      else {
        Serial.print(-1);
      }
      Serial.print("\t");
      if(read_sense2 != -1) {
        Serial.print(read_sense2);
      }
      else {
        Serial.print(-1);
      }
      Serial.println();
  }
  
  int value = analogRead(A0);
  int value2 = analogRead(A1);  
  
  if(manual && (millis() - manualtime) > 10) {
    manualtime = millis();
    int send1 = -1;
    int send2 = -1;
    if( abs(target-value) > manual_precision) {
      send1 = value;
      target = value;
    }
    if( abs(target2-value2) > manual_precision) {
      send2 = value2;
      target2 = value2;
    }
    if(send1 != -1 || send2 != -1) {
      Serial.print("S\t");
      Serial.print(send1);
      Serial.print("\t");
      Serial.println(send2);
      //delay(10);
    }
  }
  else if(!manual) {
    if (value < target - precision && (reverse || motorstop)) {
      reverse = !reverse;
      //setMotor(255, reverse);
      setMotor(downStrength, !updir); //uses the own weight of noisa
      motorstop = false;
    } else if (value > target + precision && (!reverse || motorstop)) {
      reverse = !reverse;
      setMotor(255, updir);
      motorstop = false;
    } else if (abs(value - target) < precision/2 && !motorstop) {
      setMotor(stopStrength, updir);
      motorstop = true;
    }
    
    if (value2 < target2 - precision && (reverse2 || motorstop2)) {
      reverse2 = !reverse2;
      //setMotor(255, reverse);
      setMotor2(downStrength, !updir); //uses the own weight of noisa
      motorstop2 = false;
    } else if (value2 > target2 + precision && (!reverse2 || motorstop2)) {
      reverse2 = !reverse2;
      setMotor2(255, updir);
      motorstop2 = false;
    } else if (abs(value2 - target2) < precision/2 && !motorstop2) {
      setMotor2(stopStrength, updir);
      motorstop2 = true;
    }
  }
  //delay(1);
}

void setMotor(int speed, boolean reverse)
{
  analogWrite(enablePin, speed);
  digitalWrite(in1Pin, ! reverse);
  digitalWrite(in2Pin, reverse);
}
void setMotor2(int speed, boolean reverse)
{
  analogWrite(enablePin2, speed);
  digitalWrite(in1Pin2, ! reverse);
  digitalWrite(in2Pin2, reverse);
}
