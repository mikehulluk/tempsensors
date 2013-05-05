#! /usr/bin/python


import sys
import os
import time
import shutil
import numpy as np
import datetime
import random 

os.chdir('/home/pi/tempsensors/')

import temperature_utils



sensor_addresses = [
# In Depth order
"/sys/bus/w1/devices/28-000004623b55/w1_slave",
"/sys/bus/w1/devices/28-00000462c0e6/w1_slave",
"/sys/bus/w1/devices/28-00000462a81e/w1_slave",
"/sys/bus/w1/devices/28-0000046243e9/w1_slave",
"/sys/bus/w1/devices/28-00000462c82b/w1_slave",
"/sys/bus/w1/devices/28-000004623232/w1_slave",
"/sys/bus/w1/devices/28-00000462f30a/w1_slave",
"/sys/bus/w1/devices/28-00000462dfd4/w1_slave",
"/sys/bus/w1/devices/28-00000462a3a9/w1_slave",
"/sys/bus/w1/devices/28-00000461e49a/w1_slave",


#"/sys/bus/w1/devices/28-00000461e49a/w1_slave",
#"/sys/bus/w1/devices/28-00000462a3a9/w1_slave",
#"/sys/bus/w1/devices/28-00000462c82b/w1_slave",
#"/sys/bus/w1/devices/28-000004623232/w1_slave",
#"/sys/bus/w1/devices/28-00000462a81e/w1_slave",
#"/sys/bus/w1/devices/28-00000462dfd4/w1_slave",
#"/sys/bus/w1/devices/28-0000046243e9/w1_slave",
#"/sys/bus/w1/devices/28-00000462c0e6/w1_slave",
#"/sys/bus/w1/devices/28-00000462f30a/w1_slave",



#    "/sys/bus/w1/devices/28-00000461e49a/w1_slave",
#    "/sys/bus/w1/devices/28-00000462a81e/w1_slave",
#    "/sys/bus/w1/devices/28-000004623b55/w1_slave",
#    "/sys/bus/w1/devices/28-00000462dfd4/w1_slave",
#    "/sys/bus/w1/devices/28-00000462a81e/w1_slave",
#    "/sys/bus/w1/devices/28-00000462f30a/w1_slave",

]

# Clear the log file
temp_log_file = 'temp_log_file.log'
with open(temp_log_file,'w'):
    pass



class BadW1Read(Exception):
	def __init__(self, sensorname, text):
		self.sensorname = sensorname
		self.text = text

def get_temperature(src):


    with open(src) as s1:
        d = s1.read()

    
    with open(temp_log_file,'a') as f:
       f.write('Reading from: %s\n'%src)
       f.write('At t=%s\n'%datetime.datetime.now() )
       f.write(d)
       f.write('\n\n')

    is_ok = d.split('\n')[0].split(' ')[11] == 'YES'
    
    add_random_noise= False
    if add_random_noise:
        if random.randint(0,10) == 1:
            is_ok = False

    if not is_ok:
        raise BadW1Read(sensorname=src, text=d)
    
    t = d.split('\n')[1].split(" ")[9].split('=')[1]
    return float(t)/1000.

def _get_temperature(src):
    return np.random.random()






def main():
    import temperature_db
    import temperature_db as tdb
    session = temperature_db.Session()

    # Start by consolidation:
    import consolidate_db
    consolidate_db.consolidate_db(session=session)

    # Sensor objects:
    sensors = []
    for sensor_address in sensor_addresses:
        sensors.append( (sensor_address, temperature_db.Sensor.get_or_create(address=sensor_address, session=session) ) )

    # Print Sensors found:
    for sensor in session.query(temperature_db.Sensor).all():
        print sensor

    # Main loop:
    print 'Starting main loop'
    t_start = temperature_utils.get_time() 
    t=None
    while True:
        # Pause:
        #time.sleep(1)
        t_prev = t
        t = temperature_utils.get_time()


        # Update all the temperature recordings:
        temps = []
        for sensor_address, sensor in sensors:
            
            try:
                temp = get_temperature(sensor_address)
                temps.append(temp)

                rec = temperature_db.RawRecording(sensor = sensor, time = t, temperature=temp)
                session.add(rec)

            except BadW1Read, e:
                print 'Error on:', sensor_address
                err = temperature_db.ErrorRecording(sensor = sensor, time = t, text=e.text)
                session.add(err)

        # Write to the database
        session.commit()


        # Update the display:
        print '\rRecording (t=%d) [%s]' % ((t-t_start), ', '.join(('%2.2f'%t if t is not None else 'ERR') for t in temps ) ) ,




        if t_prev is not None:
            dt_prev = datetime.datetime.fromtimestamp(t_prev)
            dt = datetime.datetime.fromtimestamp(t)
            
            # Have we written the daily database?
            if dt_prev.day != dt.day:
                db_new_fname = tdb.db_file + dt_prev.isoformat()
                print 'Writing database as: %', db_new_fname
                shutil.copyfile(tdb.db_file, db_new_fname)
                db_working = tdb.db_file + '.working'
                if os.path.exists(db_working):
                        os.unlink(db_working)
                os.symlink(db_new_fname, db_working)
            
            # Have we consolidated the database?
            if dt_prev.hour != dt.hour:
                import consolidate_db
                consolidate_db.consolidate_db(session=session)

        sys.stdout.flush()

if __name__=='__main__':
    main()
