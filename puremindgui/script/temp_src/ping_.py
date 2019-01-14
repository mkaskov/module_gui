# Run this on the PC that want to check if other PC is online.
from socket import *

def pingit():                               # defining function for later use

    s = socket(AF_INET, SOCK_STREAM)         # Creates socket
    host = '192.168.1.213' # Enter the IP of the workstation here
    port = 11312                # Select port which should be pinged

    try:
        s.connect((host, port))    # tries to connect to the host
    except: # if failed to connect
        print("Server offline")    # it prints that server is offline
        s.close()                  #closes socket, so it can be re-used
        exit()  # restarts whole process

    while True:                    #If connected to host
        print("Connected!")        # prints message
        s.close()                  # closes socket just in case
        exit()                     # exits program

pingit()                           #Starts off whole proces