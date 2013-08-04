


from sensor_reader_proxy import SensorReaderProxy as SensorReader

import pandas
import numpy as np
import pylab
import glob
import os
import bisect
import datetime

sensors = SensorReader()







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


    @classmethod
    def ensure_file_location_exists(cls, fname):
        dname = os.path.dirname(fname)
        if not os.path.exists(dname):
            os.makedirs(dname)

    def write_dataframe_to_disk(self):
        pydatetimes = self.daily_data_frame.index.to_pydatetime( )
        assert pydatetimes[0].day == pydatetimes[-1].day
        date_string =  pydatetimes[0].strftime("%Y-%m-%d")

        #print "Writing dataframe to disk for ",date_string
        output_file = 'output/daily/raw/%s.hdf5' % date_string
        SensorDataCache.ensure_file_location_exists(output_file)
        with pandas.get_store(output_file) as store:
            store['sensor_data'] = self.daily_data_frame
        os.path.getsize(output_file)
        #print " -- %s (Size: %2.2fMB)" % (output_file, float( os.path.getsize(output_file) ) /1e6 )

        down_sample = self.daily_data_frame.resample('5min')
        excel_output_file = 'output/daily/sample_5min/excel/%s.xls' % date_string
        SensorDataCache.ensure_file_location_exists(excel_output_file)
        down_sample.to_excel(excel_output_file)





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






class DataConsolidator(object):


    def __init__(self,):
        self._cached_filenames = set()
        self._cached_ranges = []
        self.raw_dir = 'output/daily/raw/'


    def update_cache(self):
        print 'Updating cache:'
        for filename in sorted(glob.glob(self.raw_dir + "*.hdf5")):
            if filename in self._cached_filenames:
                print '(Existing: %s)' % filename
                continue

            with pandas.get_store(filename) as store:
                print 'New File:', filename
                print store['sensor_data']
                times = store['sensor_data'].index.to_pydatetime()
                self._cached_ranges.append( (filename, times[0], times[-1] ) )
                self._cached_filenames.add(filename)

        # Sanity check - are we still in order?
        prev = None
        for cache in self._cached_ranges:
            assert cache[1] < cache[2]
            if prev:
                assert prev[2] < cache[1]
            prev = cache

    def get_filenames_in_range(self, start, end):
        i0 = bisect.bisect_left( [f[1] for f in self._cached_ranges], start)
        i1 = bisect.bisect_right([f[2] for f in self._cached_ranges], end )
        return [f[0] for f in self._cached_ranges][i0:i1]



    def load_filenames_into_dataframe(self, filenames):
        data_frames = []
        for filename in filenames:
            with pandas.get_store(filename) as store:
                data_frames.append(store['sensor_data'])
        return pandas.concat(data_frames)




    def build_monthly_data(self, year, month):
        print 'Building monthly data'
        self.update_cache()
        start = datetime.datetime(year=year, month=month, day=1)
        end = datetime.datetime(year=year, month=month+1, day=1)

        month_fnames = self.get_filenames_in_range( start, end )


        print month_fnames

        df = self.load_filenames_into_dataframe(month_fnames)
        
        
        date_string = "%d-%d"% (year, month)
        down_sample = df.resample('5min')
        excel_output_file = 'output/monthly/sample_5min/excel/%s.xls' % date_string
        SensorDataCache.ensure_file_location_exists(excel_output_file)
        down_sample.to_excel(excel_output_file)

        print df
        assert False









data_consolidator = DataConsolidator()
last_state = None
sensor_data_cache = SensorDataCache()
for i in range(5000000):
    sensor_state = sensors.read()
    sensor_data_cache.add(sensor_state)

    if last_state is not None and last_state.timestamp.month != sensor_state.timestamp.month:
        data_consolidator.build_monthly_data(last_state.timestamp.year, last_state.timestamp.month)


    last_state = sensor_state






#print sensor_data_cache.daily_data_frame

#sensor_data_cache.daily_data_frame.plot()


##time = daily_data_frame['time']
#print np.array( time )
#
#
#pylab.plot( time, daily_data_frame['S0'], label='S0')
#pylab.plot( time, daily_data_frame['S1'], label='S1')
#pylab.plot( time, daily_data_frame['S2'], label='S2')
#pylab.legend()
pylab.show()




