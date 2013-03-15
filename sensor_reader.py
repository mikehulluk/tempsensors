
import sys
import os
import time
import numpy as np

sensor_addresses = [
"/sys/bus/w1/devices/28-000004623b55/w1_slave",
]


def _get_temperature(src):
    with open(s1_src) as s1:
        d = s1.read()
    t = d.split('\n')[1].split(" ")[9].split('=')[1]
    return float(t)/1000.

def get_temperature(src):
    return np.random.random()






def main():
    import temperature_db
    session = temperature_db.Session()

    # Sensor objects:
    sensors = {}
    for sensor_address in sensor_addresses:
        sensors[sensor_address] = temperature_db.Sensor.get_or_create(address=sensor_address, session=session)

    # Print Sensors found:
    for sensor in session.query(temperature_db.Sensor).all():
        print sensor

    # Main loop:
    t_start = int(time.time())
    while True:
        # Pause:
        time.sleep(1)
        t = int(time.time())


        # Update all the temperature recordings:
        temps = []
        for sensor_address, sensor in sensors.items():
            temp = get_temperature(sensor_address)
            temps.append(temp)

            rec = temperature_db.Recording(sensor = sensor, time = t, temperature=temp)
            session.add(rec)

        # Write to the database
        session.commit()


        # Update the display:
        print '\rRecording (t=%d) [%s]' % ((t-t_start), ','.join('%2.2f'%t for t in temps ) ) ,

        sys.stdout.flush()

if __name__=='__main__':
    main()
