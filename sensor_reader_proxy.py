

from sensor_reader import SensorReader, SensorReadData
import random
import datetime



class SensorReaderProxy(SensorReader):

    def __init__(self):
        super(SensorReaderProxy, self).__init__()
        self.last_time = datetime.datetime.now()
        #self.dt = datetime.timedelta(seconds=5)
        self.dt = datetime.timedelta(seconds=50)
        #self.dt = datetime.timedelta(hours=3)
        self.p_error = 0.1
        self.sensor_values = { sensor:20 for sensor in self.sensor_configs }


        

    def read(self):
        # Update internal state:
        self.last_time += self.dt
        self.sensor_values = {sensor:temp+random.normalvariate(0,0.2) for (sensor,temp) in self.sensor_values.items()}

        sensor_read = [ (sensor, (self.sensor_values[sensor] if random.uniform(0,1) > self.p_error else None)) for sensor in self.sensor_configs ]
        
        results = SensorReadData(timestamp = self.last_time,
                temperatures =  sensor_read
                )

        return results

