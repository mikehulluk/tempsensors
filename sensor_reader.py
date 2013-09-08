

from configobj import ConfigObj






class SensorInfo(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        print self
    def __str__(self):
        return "<SensorInfor: %s (address=%s)>" % (self.name, self.address)


class SensorReadData(object):
    def __init__(self, timestamp, temperatures):
        self.timestamp = timestamp
        self.temperatures = temperatures

    def __str__(self):
        return "<SensorReadData: Time:%s %s>" %(self.timestamp, ",".join(["%s=%f"%(sensor.name, temp) for (sensor,temp) in self.temperatures]) )

    


class SensorReader(object):

    def __init__(self):
        self.sensor_configs = self.load_sensor_info()

    def read(self):
        """ Returns a SensorReadData object"""
        raise NotImplementedError()


    def load_sensor_info(self):
        filename = "sensorconfig.rc"
        config = ConfigObj(filename)
        sensors = [SensorInfo(name=name, **sensor_data) for name, sensor_data in config['sensors'].items()]
        return sensors
