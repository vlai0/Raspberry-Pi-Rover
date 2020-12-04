# Rover (CS121 Final Project)

A python flask app to host a website that is used to control our rover

## Installation
To install flask enter:
```
pip3 install flask
```

To enable the camera and temp sensors enter:
```
sudo raspi-config
```
For camera select Interfacing Options -> Camera and follow any on screen instructions

For temperature sensor select Interfacing Options -> I2C and follow any onscreen instructions

## Usage
Control the rover with the onscreen joystick (touchscreen compatible) or the WASD keys. The buttons on the side are used to measure temperature and distance.

## Files
* app.py is used to control the GPIO pins and power the physical rover.
* controls.js is used to determine what routes/functions to call depending on input from the website and update it with the Initial State data.
* controls.html is used to display the website and its elements.
* style.css is the stylesheet for controls.html