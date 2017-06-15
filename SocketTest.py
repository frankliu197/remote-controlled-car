import socket
PASSWORD = "password"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#change the ip address down here
s.connect(("12.200.129.202", 8000))

#give the password
s.recv(200)
s.send(PASSWORD)

#constant direction_values used in this program
direction_values = ["FORWARDS", "BACKWARDS", "LEFT", "RIGHT", "STOP"]

#Parses your direction variable that you give in and returns the direction value that is used throughout the program. Returns False if the direction_value typed is invalid
def correct_direction(direction):
    # Removes all spaces and _ and the new line characters
    direction = direction.rstrip().lstrip().lower().replace(" ", "").replace("_", "")

	#direction given by index number + 1 in direction_values
    if direction == "f" or direction == "forwards" or direction == "forward":
        direction = 1
    elif direction == "b" or direction == "backwards" or direction == "backward":
        direction = 2
    elif direction == "tl" or direction == "turnleft" or direction == "left" or direction == "l":
        direction = 3
    elif direction == "tr" or direction == "turnright" or direction == "right" or direction == "r":
        direction = 4
    elif direction == "s" or direction == "stop":
        direction = 5
    else:
        return False
    return direction

#Parses the speed variable given and returns it. It returns false if speed is not a valid speed
def correct_speed(speed):
    try:
        speed = int(speed)
        if(speed >= 0 and speed <= 100):
            return speed
    except ValueError:
        pass
    return False


while True:

    #get the direction that the user wants
    direction = None
    while not direction:
        if direction == None:
            print( "Type the direction that you want the car to go.\nChoices of FORWARDS, BACKWARDS, TURN LEFT and TURN RIGHT")
        else:
            print("Error. Invalid direction. Please Type the direction again")

        direction = correct_direction(raw_input())
    
    #send direction index number
    s.send(str(direction - 1))

    #get the speed that the user wants
    speed = None
    
    #if they siad stop. Note that speed will not matter in this case
    if direction == 5:
        speed = 10

    while not speed:
        if speed == None:
            print("The speed? Ranges from 0 - 100")
        else:
            print("Error. Invalid speed")

        speed = correct_speed(raw_input())

    print("Changing the car's speed and direction")
    
    #send speed
    s.send(str(speed))
