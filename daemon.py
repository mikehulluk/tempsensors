


from sensor_reader_proxy import SensorReaderProxy as SensorReader

import pandas
import numpy as np
import pylab
import glob
import os
import bisect
import datetime

sensors = SensorReader()





class SensorDataWriter(object):
        #os.path.getsize(output_file)
        ##print " -- %s (Size: %2.2fMB)" % (output_file, float( os.path.getsize(output_file) ) /1e6 )
    @classmethod
    def write_hdf5_raw(cls, dataframe, filename):
        SensorDataCache.ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_hdf5_5min(cls, dataframe, filename):
        dataframe = dataframe.resample('5min')
        SensorDataCache.ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_hdf5_1hr(cls, dataframe, filename):
        dataframe = dataframe.resample('60min')
        SensorDataCache.ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_excel_raw(cls, dataframe, filename):
        SensorDataCache.ensure_file_location_exists(filename)
        dataframe.to_excel(filename)
    @classmethod
    def write_excel_5min(cls, dataframe, filename):
        dataframe = dataframe.resample('5min')
        SensorDataCache.ensure_file_location_exists(filename)
        dataframe.to_excel(filename)
    @classmethod
    def write_excel_1hr(cls, dataframe, filename):
        dataframe = dataframe.resample('60min')
        SensorDataCache.ensure_file_location_exists(filename)
        dataframe.to_excel(filename)




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
        # Write to HDF5:
        SensorDataWriter.write_hdf5_raw( self.daily_data_frame,  'output/daily/raw/hdf5/%s.hdf5' % date_string )
        SensorDataWriter.write_hdf5_5min( self.daily_data_frame, 'output/daily/5min/hdf5/%s.hdf5' % date_string)
        SensorDataWriter.write_hdf5_1hr( self.daily_data_frame,  'output/daily/1hr/hdf5/%s.hdf5' % date_string)


        #SensorDataWriter.write_excel_raw( self.daily_data_frame,  'output/daily/raw/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_5min( self.daily_data_frame, 'output/daily/5min/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_1hr( self.daily_data_frame,  'output/daily/1hr/excel/%s.xls' % date_string)






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






class HDFStoreCache(object):
    def __init__(self, downsample):
        self._cached_filenames = set()
        self._cached_ranges = []
        self.downsample = downsample
        self.raw_dir = 'output/daily/%s/hdf5/' % downsample


    def update_cache(self):
        print 'Updating cache:'
        print 'glob_string', self.raw_dir + "*.hdf5"
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





class DataConsolidator(object):
    def __init__(self,):
        self._store_cache = {}

    def get_uptodate_store_cache(self, downsample):
        if not downsample in self._store_cache:
            self._store_cache[downsample] = HDFStoreCache(downsample)
        self._store_cache[downsample].update_cache()
        return self._store_cache[downsample]

    def load_filenames_into_dataframe(self, filenames, starttime, endtime):
        data_frames = []
        for filename in filenames:
            with pandas.get_store(filename) as store:
                fr = store['sensor_data']
                mask = (fr.index>=starttime) & (fr.index<endtime)
                data_frames.append(fr[mask])
        df = pandas.concat(data_frames)
        return df







    def build_monthly_data(self, year, month, src_downsample):
        print 'Building monthly data'
        start = datetime.datetime(year=year, month=month, day=1)

        if month!=12:
            end = datetime.datetime(year=year, month=month+1, day=1)
        else:
            end = datetime.datetime(year=year+1, month=1, day=1)

        month_fnames = self.get_uptodate_store_cache(downsample=src_downsample).get_filenames_in_range(start, end )
        print month_fnames
        print 'Loading New dataframe'
        df = self.load_filenames_into_dataframe(month_fnames, start, end)


        date_string = "%d-%02d"% (year, month)
        SensorDataWriter.write_excel_5min( df, 'output/monthly/5min/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_1hr( df, 'output/monthly/1hr/excel/%s.xls' % date_string)

        return df







def main():

    data_consolidator = DataConsolidator()
    last_state = None
    sensor_data_cache = SensorDataCache()
    for i in range(5000000):
        sensor_state = sensors.read()
        sensor_data_cache.add(sensor_state)

        if last_state is not None and last_state.timestamp.month != sensor_state.timestamp.month:
            data_consolidator.build_monthly_data(last_state.timestamp.year, last_state.timestamp.month, src_downsample='5min')


        last_state = sensor_state


if __name__=='__main__':
    main()








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




