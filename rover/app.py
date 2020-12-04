from flask import Flask, render_template, Response
from multiprocessing import Process
import RPi.GPIO as GPIO
import smbus
from ISStreamer.Streamer import Streamer
import time
from camera_pi import Camera #Miguel Grinberg's pi camera implementation

app = Flask(__name__)

BUS = smbus.SMBus(1)
ADDRESS = 0x48

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#to stop twitching
global isStraight
isStraight=True


#ultrasonic sensor info
SPEED_OF_SOUND= 17150 #cm per second
THRESHHOLD = 5 #cm

#define pin numbers here 
DRIVE_PIN = 8
DRIVE_PIN_TWO = 11
REVERSE_PIN = 10
REVERSE_PIN_TWO = 13
SERVO_PIN = 40
LEFT_BLINKER_PIN = 16
RIGHT_BLINKER_PIN = 18
DIST_IN_PIN = 24
DIST_OUT_PIN = 22

#set up pins
GPIO.setup(DRIVE_PIN, GPIO.OUT)
GPIO.setup(DRIVE_PIN_TWO, GPIO.OUT)
GPIO.setup(REVERSE_PIN, GPIO.OUT)
GPIO.setup(REVERSE_PIN_TWO, GPIO.OUT)
GPIO.setup(RIGHT_BLINKER_PIN, GPIO.OUT)
GPIO.setup(LEFT_BLINKER_PIN, GPIO.OUT)
GPIO.setup(DIST_OUT_PIN, GPIO.OUT)
GPIO.setup(DIST_IN_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)
p = GPIO.PWM(SERVO_PIN, 50) #not sure about the 50Hz, range is from 2-12, 7 straight
p.start(7) #initialize it to halfway
time.sleep(1)
p.ChangeDutyCycle(0)


#driving controls
@app.route("/drive", methods=["POST"])
def drive():
    GPIO.output(DRIVE_PIN, GPIO.HIGH)
    GPIO.output(DRIVE_PIN_TWO, GPIO.HIGH)
    return "drive"

@app.route("/reverse", methods=["POST"])
def reverse():
    GPIO.output(REVERSE_PIN, GPIO.HIGH)
    GPIO.output(REVERSE_PIN_TWO, GPIO.HIGH)
    return "reverse"


@app.route("/neutral", methods=["POST"])
def neutral():
    GPIO.output(DRIVE_PIN, GPIO.LOW)
    GPIO.output(DRIVE_PIN_TWO, GPIO.LOW)
    GPIO.output(REVERSE_PIN, GPIO.LOW)
    GPIO.output(REVERSE_PIN_TWO, GPIO.LOW)
    return "neutral"

@app.route("/left", methods=["POST"])
def left():
    global isStraight
    isStraight = False
    GPIO.output(LEFT_BLINKER_PIN, GPIO.HIGH)
    p.ChangeDutyCycle(9) #for now idk how far it should go, 2 would be 180 since the servo is upside down right
    return "left"

@app.route("/right", methods=["POST"])
def right():
    global isStraight
    isStraight = False
    GPIO.output(RIGHT_BLINKER_PIN, GPIO.HIGH)
    p.ChangeDutyCycle(6)
    return "right"

@app.route("/straight", methods=["POST"])
def straight():
    global isStraight
    if isStraight:
        return "straight"
    GPIO.output(LEFT_BLINKER_PIN, GPIO.LOW)
    GPIO.output(RIGHT_BLINKER_PIN, GPIO.LOW)
    p.ChangeDutyCycle(7)
    time.sleep(0.2)
    p.ChangeDutyCycle(0) #so it doesn't jitter
    isStraight = True
    return "straight"

@app.route("/get_temp", methods=["POST"])
def get_temperature():
    rvalue0 = BUS.read_word_data(ADDRESS,0)
    rvalue1 = (rvalue0 & 0xff00) >> 8
    rvalue2 = rvalue0 & 0x00ff
    rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625

    streamer = Streamer(
    bucket_name="rover temp",
    bucket_key="QX7Q9AQQDRKD",
    access_key="ist_oGJn5sxm28Wnq1w7RVul0NiZ96PNa4lN"
    )

    streamer.log("rover temp", rvalue)
    streamer.flush()
    
    return "temp logged"

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

    streamer = Streamer(
    bucket_name="rover dist",
    bucket_key="GXCWSBWT9KH8",
    access_key="ist_oGJn5sxm28Wnq1w7RVul0NiZ96PNa4lN"
    )

    streamer.log("Dist", (pulse_end - pulse_start) * SPEED_OF_SOUND)
    streamer.flush()

    return "Distance measured"

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
