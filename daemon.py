


from sensor_reader_proxy import SensorReaderProxy as SensorReader

import pandas
import numpy as np
import pylab
import glob
import os
import bisect
import datetime

sensors = SensorReader()


from datastore import HDFStoreCache, DataConsolidator, SensorDataWriter





class SensorDataCache(object):
    def __init__(self):
        self.unprocessed_sensor_states = []
        self.daily_data_frame = None


    def write_cache_to_data_frame(self):
        # A. Create into a new data_frame:
        # ( Convert into {'S0': [....], 'S1': [....] ...}
        sensor_data = { sensor.name: [ sensor_state.temperatures[index][1] for sensor_state in self.unprocessed_sensor_states]  for index, sensor in enumerate(sensors.sensor_configs) }
        times = [ sensor_state.timestamp for sensor_state in self.unprocessed_sensor_states]
        new_data_frame = pandas.DataFrame( sensor_data, times )

        # B. Append to the data frame:
        if self.daily_data_frame is None:
            self.daily_data_frame = new_data_frame
        else:
            self.daily_data_frame = pandas.concat([self.daily_data_frame, new_data_frame])

        # C. Clear the list of unprocessed_sensor_states:
        self.unprocessed_sensor_states = []



    def write_dataframe_to_disk(self):
        pydatetimes = self.daily_data_frame.index.to_pydatetime( )
        assert pydatetimes[0].day == pydatetimes[-1].day
        date_string =  pydatetimes[0].strftime("%Y-%m-%d")

        #print "Writing dataframe to disk for ",date_string
        # Write to HDF5:
        SensorDataWriter.write_hdf5_raw( self.daily_data_frame,  'output/daily/raw/hdf5/%s.hdf5' % date_string )
        SensorDataWriter.write_hdf5_5min( self.daily_data_frame, 'output/daily/5min/hdf5/%s.hdf5' % date_string)
        SensorDataWriter.write_hdf5_1hr( self.daily_data_frame,  'output/daily/1H/hdf5/%s.hdf5' % date_string)


        #SensorDataWriter.write_excel_raw( self.daily_data_frame,  'output/daily/raw/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_5min( self.daily_data_frame, 'output/daily/5min/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_1hr( self.daily_data_frame,  'output/daily/1H/excel/%s.xls' % date_string)






    def add(self, sensor_state):

        # Is it a new day:
        if (self.unprocessed_sensor_states and  sensor_state.timestamp.day != self.unprocessed_sensor_states[0].timestamp.day):

            print 'New day:', sensor_state.timestamp
            self.write_cache_to_data_frame()
            self.write_dataframe_to_disk()
            self.daily_data_frame = None

        self.unprocessed_sensor_states.append(sensor_state)


        if len(self.unprocessed_sensor_states) > 200:
            self.write_cache_to_data_frame()











def do_rundaemon():

    data_consolidator = DataConsolidator()
    last_state = None
    sensor_data_cache = SensorDataCache()
    for i in range(5000000):
        sensor_state = sensors.read()
        sensor_data_cache.add(sensor_state)

        if last_state is not None and last_state.timestamp.month != sensor_state.timestamp.month:
            data_consolidator.build_monthly_data(src_downsample='5min',  year=last_state.timestamp.year, month=last_state.timestamp.month)

        last_state = sensor_state


if __name__=='__main__':
    do_rundaemon()




