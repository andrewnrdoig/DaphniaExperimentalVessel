import datetime #imports the time utilities
import time
import csv
import os
import glob
import RPi.GPIO as GPIO #Necessary for GPIO on Pie
from picamera import PiCamera

##################################################################################################################################################

##################################################################################################################################################
#initialize temperature sensor

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
##################################################################################################################################################

################################################################################################################################
#Create camera object

camera = PiCamera()
camera.resolution = (2592,1944)
camera.start_preview()


##################################################################################################################################################
lamp = "off" #Creates global lamp object to monitor lamp status
##################################################################################################################################################

##################################################################################################################################################
#Set output pins for relay to control lamp
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.HIGH)   # Set pin 8 to be an output pin and set initial value to low (off)
##################################################################################################################################################

##################################################################################################################################################

def habitatLampStartTime():
    #create the lamp time start with user input
    #poll user for time information
    polluserStartHour, polluserStartMinute = [int(polluserStartHour) for polluserStartHour in input("Please enter lamp start hour and minute (00 00): ").split()]
    #generate a time object that will be the time to start the lamp
    lampStartTime = datetime.time(polluserStartHour, polluserStartMinute,0,0)
    #Get values out of the function
    habitatLampStartTime.lampStartMinute = lampStartTime.minute
    habitatLampStartTime.lampStartHour = lampStartTime.hour
    #Report Lamp Start Time
    print('lampStartTime is set to:',lampStartTime)

def habitatLampStopTime():
    #create the lamp stop time with user input
    #poll user for time information
    polluserStopHour, polluserStopMinute = [int(polluserStopHour) for polluserStopHour in input("Please enter lamp stop hour and minute (00 00): ").split()]
    #generate a time object that will be the time to start the lamp
    lampStopTime = datetime.time(polluserStopHour, polluserStopMinute,0,0)
    #Get values out of the function
    habitatLampStopTime.lampStopMinute = lampStopTime.minute
    habitatLampStopTime.lampStopHour = lampStopTime.hour
    #Report the lamp stop times
    print('lampStopTime is set to: ',lampStopTime)
   
#Reading the remperature data raw from the sensor    
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
#Converting the temperature to human readable forms
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
   
   
######################################################################



   
##################################################################################################################################################
#Set start and stop times for run cycle
print("Hello, you are initializing the automated Daphnia Experiment Vessel, or D.E.V.")
habitatLampStartTime() #Create a habitatLampStartTime, which is the time each day to start the lamp
habitatLampStopTime()  #Create a habitatLampStopTime, which is the time each day to stop the lamp
##################################################################################################################################################    


##################################################################################################################################################
#main control loop
while True:
   
   
#Codeblock for generating a new folder everyday

    currentDate = datetime.date.today() #get current date in an object
    currentDateString = currentDate.strftime("%m-%d-%Y") #sets date to a string for parsing file names

#Check to see if the folder for today exists
    current_directory = os.getcwd()
    home_directory = '/home/pi/Desktop/DEV Box/Code/Version 11 Environment/Home'

    if current_directory != home_directory:
        os.chdir("..")
         
    does_exist = os.path.isdir('./%s' % currentDateString)

    if does_exist == False:
        path = "./%s" % currentDateString
        os.mkdir(path)
   
        does_exist = os.path.isdir('./%s' % currentDateString)

    if does_exist == True:
       os.chdir('./%s' % currentDateString)
   
    #DirectoryManagement()
    print(os.getcwd())
    currentLocalDateandTime = datetime.datetime.now() #creates an object that records the current time
    stringCurrentLocalDateandTime = currentLocalDateandTime.strftime("%m-%d-%Y, %H:%M:%S") #Generate current date and time as string for writing to text file
    print('Current time:',currentLocalDateandTime) #reports the current time at running the lamp off or on logic
   
    if habitatLampStartTime.lampStartMinute == currentLocalDateandTime.minute and habitatLampStartTime.lampStartHour == currentLocalDateandTime.hour:
        lamp = "on"
        GPIO.output(8, GPIO.LOW)  # Turn on lamp
        print('Lamp is: ', lamp)

    if habitatLampStopTime.lampStopMinute == currentLocalDateandTime.minute and habitatLampStopTime.lampStopHour == currentLocalDateandTime.hour:
        lamp = "off"
        GPIO.output(8, GPIO.HIGH)    # Turn off lamp
        print('Lamp is: ', lamp)
       
    print("Probe temp in Cent. & Faren. is: ", read_temp())#report temperature in command line
   
    #Codeblock for generating a new data file every day
    currentDate = datetime.date.today() #get current date in an object
    currentDateString = currentDate.strftime("%m-%d-%Y") #sets date to a string for parsing file names
    fileIsText = ".txt"
    currentFileName = currentDateString + fileIsText

    #Codeblock for adding data to file
    new_line = "\n" #read the tin
    writtenState = False
   
    while writtenState != True: #Flag that tracks whether we wrote the data to the file
           
       
            with open(currentFileName, 'a') as dataFile: #opens or creates a daily data file
                dataFile_writer = csv.writer(dataFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL) #sets the qualities of the datafile writer
                dataFile_writer.writerow([datetime.datetime.now(), lamp, read_temp()]) #append fields/column names to document
            writtenState = True        
           
    #Codeblock for photographing tank every sampling    
    camera.capture("%s.jpg" % stringCurrentLocalDateandTime)

   
    time.sleep(1800)#Sleep the control loop for 30 minutes until next cycle
