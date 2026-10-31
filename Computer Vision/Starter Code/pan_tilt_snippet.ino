// pan_tilt_snippet.ino - add to the ESP32-CAM "CameraWebServer" example.
// Pan servo signal on GPIO 13, tilt servo signal on GPIO 14 (avoid GPIO 12/15/0/2: boot-strapping pins).
// Servos need their OWN 5 V supply (>=1 A) with GND joined to the ESP32-CAM GND, plus a 470-1000 uF capacitor.
#include <ESP32Servo.h>
Servo panServo, tiltServo;
const int PAN_PIN = 13, TILT_PIN = 14;

void setupServos() {
  // the camera clock already uses LEDC timer 0, so give the servos other timers
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  panServo.setPeriodHertz(50);  panServo.attach(PAN_PIN, 500, 2400);
  tiltServo.setPeriodHertz(50); tiltServo.attach(TILT_PIN, 500, 2400);
  panServo.write(90); tiltServo.write(90);
}
// Then add an HTTP handler such as  /look?pan=60&tilt=100  that calls
// panServo.write(constrain(pan,0,180)); tiltServo.write(constrain(tilt,40,140));
// (ask your AI tool to write the handler - prompt 1.3 in the Prompt Library)
