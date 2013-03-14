


import sys
import os
import time
import numpy as np

#import temperature_db
import temperature_db as tdb
session = tdb.Session()

sensors = session.query(tdb.Sensor).all()


import matplotlib
matplotlib.use('gtkagg')
import pylab
f = pylab.figure()
ax = f.add_subplot(111)

for sensor in sensors:
    print sensor
    recs = sensor.recordings
    l = np.array([ (r.time, r.temperature) for r in recs])

    ax.plot(l[:,0], l[:,1],'x-', label='%s' % sensor.address)

ax.legend() 
pylab.show()
