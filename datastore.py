import glob
import bisect
import os
import datetime

import pandas 


import numpy as np

def ensure_file_location_exists(fname):
        dname = os.path.dirname(fname)
        if not os.path.exists(dname):
            os.makedirs(dname)




class SensorDataWriter(object):
        #os.path.getsize(output_file)
        ##print " -- %s (Size: %2.2fMB)" % (output_file, float( os.path.getsize(output_file) ) /1e6 )
    @classmethod
    def write_hdf5_raw(cls, dataframe, filename):
        ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_hdf5_5min(cls, dataframe, filename):
        dataframe = dataframe.resample('5min')
        ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_hdf5_1hr(cls, dataframe, filename):
        dataframe = dataframe.resample('1H')
        ensure_file_location_exists(filename)
        with pandas.get_store(filename) as store:
            store['sensor_data'] = dataframe

    @classmethod
    def write_excel_raw(cls, dataframe, filename):
        ensure_file_location_exists(filename)
        dataframe.to_excel(filename)
    @classmethod
    def write_excel_5min(cls, dataframe, filename):
        dataframe = dataframe.resample('5min')
        ensure_file_location_exists(filename)
        dataframe.to_excel(filename)
    @classmethod
    def write_excel_1hr(cls, dataframe, filename):
        dataframe = dataframe.resample('1H')
        ensure_file_location_exists(filename)
        dataframe.to_excel(filename)




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
        if start != None:
            i0 = bisect.bisect_left( [f[1] for f in self._cached_ranges], start)
        else:
            i0 = 0

        if end != None:
            i1 = bisect.bisect_right([f[2] for f in self._cached_ranges], end )
        else:
            i1 = len(self._cached_ranges)
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

                # This is a terrible piece of code!:
                mask1 = None
                mask2 = None
                if starttime is not None:
                    mask1 = (fr.index>=starttime)
                if endtime is not None:
                    mask2 = (fr.index<endtime)

                if mask1 is not None:
                    if mask2 is not None:
                        data_frames.append(fr[mask1 & mask2])
                    else:
                        data_frames.append(fr[mask1])
                else:
                    if mask2 is not None:
                        data_frames.append(fr[mask2])
                    else:
                        data_frames.append(fr)




        df = pandas.concat(data_frames)
        return df


    def extract_dataframe(self, src_downsample, startdate=None, enddate=None,  further_downsample=None):
        fnames = self.get_uptodate_store_cache(downsample=src_downsample).get_filenames_in_range(startdate, enddate )
        print fnames
        print 'Loading New dataframe'
        df = self.load_filenames_into_dataframe(fnames, startdate, enddate)
        return df






    def build_monthly_data(self, year, month, src_downsample):
        print 'Building monthly data'
        start = datetime.datetime(year=year, month=month, day=1)

        if month!=12:
            end = datetime.datetime(year=year, month=month+1, day=1)
        else:
            end = datetime.datetime(year=year+1, month=1, day=1)


        df = self.extract_dataframe(startdate=start, enddate=end, src_downsample=src_downsample)


        date_string = "%d-%02d"% (year, month)
        SensorDataWriter.write_excel_5min( df, 'output/monthly/5min/excel/%s.xls' % date_string)
        SensorDataWriter.write_excel_1hr( df, 'output/monthly/1hr/excel/%s.xls' % date_string)

        return df


