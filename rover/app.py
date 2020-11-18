from flask import Flask, render_template, Response
import RPi.GPIO as GPIO
import time
from camera_pi import Camera #Miguel Grinberg's pi camera implementation

app = Flask(__name__)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#ultrasonic sensor info
SPEED_OF_SOUND= 17150 #cm per second
THRESHHOLD = 5 #cm
tooClose = False

#define pin numbers here 
#take away the """ 's when youve added pin numbers
"""
DRIVE_PIN = 
REVERSE_PIN = 
SERVO_PIN =
LEFT_BLINKER_PIN = 
RIGHT_BLINKER_PIN =
DIST_IN_PIN = 
DIST_OUT_PIN = 

#set up pins
GPIO.setup(DRIVE_PIN, GPIO.OUT)
GPIO.setup(REVERSE_PIN, GPIO.OUT)
GPIO.setup(RIGHT_BLINKER_PIN, GPIO.OUT)
GPIO.setup(LEFT_BLINKER_PIN, GPIO.OUT)
GPIO.setup(DIST_OUT_PIN, GPIO.OUT)
GPIO.setup(DIST_IN_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

p = GPIO.PWM(SERVO_PIN, 50) #not sure about the 50Hz, range is from 2-12, 7 straight
p.start(7) #initialize it to halfway
time.sleep(1)
p.ChangeDutyCycle(0)

"""

#driving controls
@app.route("/drive", methods=["POST"])
def drive():
    GPIO.output(DRIVE_PIN, GPIO.HIGH)

@app.route("/reverse", methods=["POST"])
def reverse():
    GPIO.output(REVERSE_PIN, GPIO.HIGH)

@app.route("/neutral", methods=["POST"])
def neutral():
    GPIO.output(DRIVE_PIN, GPIO.LOW)
    GPIO.output(REVERSE_PIN, GPIO.LOW)

@app.route("/left", methods=["POST"])
def left():
    GPIO.output(LEFT_BLINKER_PIN, GPIO.HIGH)
    p.ChangeDutyCycle(3.5) #for now idk how far it should go, 2 would be 180 since the servo is upside down right
    time.sleep(0.2) #to give the servo time to turn before it is told to stop jittering if we want to avoid using time here we can't do the next line same for others
    p.ChangeDutyCycle(0) #so it doesn't jitter

@app.route("/right", methods=["POST"])
def right():
    GPIO.output(RIGHT_BLINKER_PIN, GPIO.HIGH)
    p.ChangeDutyCycle(10.5)
    time.sleep(0.2)
    p.ChangeDutyCycle(0) #so it doesn't jitter

@app.route("/straight", methods=["POST"])
def straight():
    GPIO.output(LEFT_BLINKER_PIN, GPIO.LOW)
    GPIO.output(RIGHT_BLINKER_PIN, GPIO.LOW)
    p.ChangeDutyCycle(7)
    time.sleep(0.2)
    p.ChangeDutyCycle(0) #so it doesn't jitter

#ultrasonic sensor
@app.route("/get_dist", methods=["POST"])
def getDist():
    time.sleep(0.5)
    GPIO.output(DIST_OUT_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(DIST_OUT_PIN, GPIO.LOW)

    while GPIO.input(DIST_IN_PIN)==0:
        pulse_start = time.time()

    while GPIO.input(DIST_IN_PIN)==1:
        pulse_end = time.time()   

    if (pulse_end - pulse_start) * SPEED_OF_SOUND < THRESHHOLD:
        tooClose = True
    else:
        tooClose = False
    
    return tooClose

#Miguel Grinberg's pi camera implementation (slightly adapted for our use)
#initializes the camera class
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#gets the image element to display it in
@app.route('/livestream')
def livestream():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/", methods=["GET"])
def home():
    return render_template("controls.html")
