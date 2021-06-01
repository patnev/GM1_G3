from events import Events
from constants import *
import numpy as np
from read_serial import SerialReader
from classes import Buffer, Meal, Event, FinishedMeal

ser = SerialReader()
buffer = Buffer(AR_LENGTH)
events = []
eventInProgress = False
ongoingMeal = Meal()

while True:
    reading = ser.readline()
    if reading == -1:
        ongoingMeal.forceToggle(buffer.latest())

    else:
        if not buffer.isFull(): 
            buffer.add(reading)
            continue
        outlier = buffer.score(reading, useTypical=eventInProgress) > OUTLIER_Z_SCORE
        if not eventInProgress:
            buffer.updateTypicalDev()
        if not eventInProgress and outlier:
            eventInProgress = True
            #print("EVENT STARTED with reading,avg, ", reading, buffer.average())
            events.append(Event([buffer.earliest()], reading))
        elif eventInProgress:
            if outlier:
                events[-1].add(reading)
            else:
                eventInProgress = False
                #print("EVENT ENDED with reading,avg, ", reading, buffer.average())
                events[-1].end()
                ongoingMeal.updateWithEvent(events[-1])
            

        buffer.add(reading)

    if ongoingMeal.checkIfIdle() or ongoingMeal.forceEnd: 
        success = ongoingMeal.endMeal(buffer.latest())
        if success == -1:
            print("Invalid Meal")
        else:
            finishedMeal = FinishedMeal(ongoingMeal)
            print(finishedMeal)
        ongoingMeal.reset()