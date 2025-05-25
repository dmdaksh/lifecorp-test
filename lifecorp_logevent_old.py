# Import the time, datetime, sys, traceback, pdb, and datetime modules
import time
import datetime
import sys
import csv
from datetime import datetime



# Define global variables to track the start time and the last time
gnStartLog = time.time()
gnLastTime = 0
gnStart = time.time()

# Define a function to get the stack trace
def Stack():
    # Return a string containing the current function name
    curframe = sys._getframe()
    stackarr = [curframe.f_code.co_name]
   
    # Continue going up the stack until the main module is reached
    while True:
        curname = curframe.f_back.f_code.co_name
        if curname == "<module>":
            break
        
        stackarr.insert(0, curname)
        curframe = curframe.f_back

    # Return the stack trace as a string
    # after removing /LogEvent/Stack/
    return '/'.join(stackarr[:-2])


# Define a function to log an event
def LogEvent(lcEvent):
    global gnStartLog
    global gnLastTime

    # Initialize variables
    lcStack = ''
    lnTime = 0
    lnEt = 0

        # Get the current datetime as a string
    now = datetime.now()
    lcDatetimeNow = now.strftime("%Y-%m-%d %H:%M:%S")
    lnTime = time.time()
    lcStack = Stack()

    lnEt = lnTime - gnStartLog
    
    gnStartLog = time.time()

    lcET = f"{lnEt:.8f}" if 'e' not in str(lnEt) else f"{lnEt:8f}"

    lcEventData = [lcEvent, lcET, lcDatetimeNow, lcStack]
    lcEvent4 = ','.join([ '"' + field + '"' for field in lcEventData]) 

     # Open the file to append
    with open('/root/walt/writer1w.csv', 'a', newline='') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(lcEventData)

    gnLastTime = time.time()
    return lcEvent4

def First(): 
    lcMyEvent = "Hello walt this is an event!"
    lcFirst= LogEvent(lcMyEvent)
    return lcFirst

lnCounter=0
while lnCounter < 100000:
    lcTopReturn=First()
    lnTotal=time.time() - gnStart
    lnCounter += 1
    
print(lnTotal)
print(lcTopReturn)


