


import sys
import os
import time
import numpy as np

#import temperature_db
import temperature_db as tdb
session = tdb.Session()

sensors = session.query(tdb.Sensor).all()



for sensor in sensors:
    print sensor
    print ' > Raw Recordings:', len(sensor.raw_recordings)
    print ' > Errors', len(sensor.errors)
    
