import socket, sys
import RPi.GPIO as GPIO
import time
import threading
import math

MAXSPEED = 100
PASSWORD = "password" #password to use this car
DRIVE_TIME = 0.05 #the minumum number I can put there for the motor to actually spin


GPIO.setmode(GPIO.BOARD)

#sets up the Pinouts of each wheel
wheel1A = 15
wheel1B = 16
wheel2A = 31
wheel2B = 32

#Wheel groups
wheels = [wheel1A, wheel1B, wheel2A, wheel2B]
wheelsA = [wheel1A, wheel2A]
wheelsB = [wheel1B, wheel2B]
wheels1 = [wheel1A, wheel1B]
wheels2 = [wheel2A, wheel2B]

GPIO.setup(wheels, GPIO.OUT)

#Returns all other wheels in a list that does not equal the the wheel given in
def other_wheels(w):
    toreturn = []
    for wheel in wheels:
        if w is not wheel:
            toreturn.append(wheel)
    return toreturn 

MID = 2;

#Direction arrays: The outputs of these pins relative to index is: [GPIO.LOW, GPIO.HIGH, MID]
#MID was used but my multithreading program failed
#I will keep the code here for convienence should i retry it
STOP = [wheels, [], []]
FORWARD = [wheelsB, wheelsA, []]
BACKWARD = [wheelsA, wheelsB, []]
RIGHT = [other_wheels(FORWARD[GPIO.HIGH][0]), [FORWARD[GPIO.HIGH][0]], []]
LEFT = [other_wheels(FORWARD[GPIO.HIGH][1]), [FORWARD[GPIO.HIGH][1]], []]
#RIGHT = [FORWARD[GPIO.LOW], [FORWARD[GPIO.HIGH][0]], [FORWARD[GPIO.HIGH][1]]]
#LEFT = [FORWARD[GPIO.LOW], [FORWARD[GPIO.HIGH][1]], [FORWARD[GPIO.HIGH][2]]]
direction_values = [FORWARD, BACKWARD, LEFT, RIGHT, STOP] #corrolates index number with its direction


#resets all the pins to not move
def reset():
    GPIO.output(wheels, GPIO.LOW)

#calculates the sleep time of the motor for a given speed
def sleeptime(speed):
    number = 0.5 - ((speed / 2.0 ** (1./3.)) * 0.10772)
    #the 0.10772 is the number that makes sleep time = 0 when speed / 2 = 100
        
    if number < 0: return 0
    else: return number

#Creating server socket using TCP protocol
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("12.200.129.202", 8000)) #change ip address here
serversocket.listen(1)

while True:
    (client, (ip, port)) = serversocket.accept()
    client.send("Password?")

    #get password to ensure its the right client
    if client.recv(200).rstrip() == PASSWORD:
        serversocket.close()
        break
    else:
       client.send("Wrong Password")
       client.close()


#insures only one thread works on the motors at once
motorlock = threading.Lock()

# this is the loop that makes the car running
class MotorThread(threading.Thread):
    def __init__(self, direction, speed):
        threading.Thread.__init__(self)
	self.direction = direction
        self.tocontinue = True
        self.sleeptime = sleeptime(speed)

    def run(self):
        motorlock.acquire()
        while self.tocontinue:
            GPIO.output(self.direction[GPIO.HIGH], GPIO.HIGH)
       	    time.sleep(DRIVE_TIME)
            GPIO.output(self.direction[GPIO.HIGH], GPIO.LOW)
            time.sleep(self.sleeptime)
	reset()
        motorlock.release()

    def stop(self):
        self.tocontinue = False
    
#await for instructions
try:
    thread = MotorThread(STOP, 0)
    while True:     
        direction = client.recv(20)
        if direction == "exit":
            client.close()
            sys.exit()
        direction = direction_values[int(direction)]
    	speed = int(client.recv(20))
        thread.stop()
    	thread = MotorThread(direction, int(speed))
    	thread.start()

except KeyboardInterrupt:
    GPIO.cleanup()
    quit()
