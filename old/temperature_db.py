
import sqlalchemy
import inspect
import os
import numpy as np
import cStringIO
import bz2
import socket
import glob 


from sqlalchemy import Column, Integer, String, Float, Text, LargeBinary, ForeignKey#, relationship, backref
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import matplotlib.dates as md
import datetime
from matplotlib import dates



def array_to_str(arr):
    op = cStringIO.StringIO()
    np.save(op, arr)
    return op.getvalue()





# Figure out the databse name, relative to this file:
module_dir = os.path.dirname( os.path.abspath(inspect.stack()[0][1]))
db_data_dir = os.path.join(module_dir, 'db_data')
if not os.path.exists(db_data_dir):
    print 'Creating DB data dir:', db_data_dir
    os.makedirs(db_data_dir)

hostname = socket.gethostname()
if hostname == 'michael-MacBookPro':
    #db_file = os.path.join(db_data_dir, 'temps.sqllite.working')

    files = sorted(glob.glob(os.path.join(db_data_dir, 'temps.sqllite2*')) )
    db_file = files[-1]
    print files[0], files[-1]

elif hostname == 'michael-GA-MA790FX-DQ6':
    db_file = 'previous_data/temps.sqllite'
elif hostname == 'raspberrypi':
    db_file = os.path.join(db_data_dir, 'temps.sqllite')
else:
    assert False


engine = sqlalchemy.create_engine('sqlite:///%s'%db_file)

Base = declarative_base()


# Classes:
class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    address = Column(String)

    @classmethod
    def get_or_create(cls, session,  address):
        r=session.query(Sensor).filter_by(address=address).all()
        if len(r) == 0:
            s = Sensor(address=address)
            session.add(s)
            session.commit()
            return s
        else:
            assert len(r) == 1
            return r[0]

    def Q_raw_recordings_in_range(self,session, start=None, end=None):
        q = session.query(RawRecording).filter( RawRecording.sensor_id == self.id)
        if start is not None:
            q = q.filter( RawRecording.time >= start) 
        if end is not None:
            q = q.filter( RawRecording.time < end) 
        return q.order_by('time')

    def get_np_array(self, session, start=None, end=None, dates_to_mpl=False):
        arrays = []

        # Get the recording-arrays:
        recording_arrays = self.recordings_arrays
        for ra in recording_arrays:
            #print ra
            data=ra.data
            #print data.shape
            arrays.append(data)


        # Get the raw_recording points:
        #print 'Raw recordings'
        Q = self.Q_raw_recordings_in_range(session=session, start=start, end=end)
        if Q.count() > 0:
            rr = np.array([ (r.time, r.temperature) for r in Q.all()])
            arrays.append(rr)

        #print 'Arrays useds'
        #for arr in arrays:
        #    print arr.shape
        final_array = np.concatenate(arrays)

        #print 'Danger, Danger, checking turned off!'
        time_diff = np.diff(final_array[:,0])
        good_times = ( time_diff > 0 )
        assert np.all(good_times)

        if dates_to_mpl:
            dts = map(datetime.datetime.fromtimestamp, final_array[:,0])
            fds = dates.date2num(dts) # converted
            final_array[:,0] = fds
        return final_array





class RawRecording(Base):
    __tablename__ = 'rawrecordings'

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    temperature = Column(Float)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))

    sensor = relationship("Sensor", backref=backref('raw_recordings', order_by=time))

    def __init__(self, sensor, time, temperature):
        self.sensor = sensor
        self.time = time
        self.temperature = temperature

    


class RecordingArray(Base):
    __tablename__ = 'recordingarrays'
    id = Column(Integer, primary_key=True)
    start_time = Column(Integer)
    end_time = Column(Integer)

    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    sensor = relationship("Sensor", backref=backref('recordings_arrays', order_by=end_time))
    
    data_bz2 = Column(LargeBinary)
    
    n_entries = Column(Integer)

    def __init__(self, sensor,  data):
        #print data.shape
        assert len(data.shape) == 2
        assert data.shape[1] == 2
        assert data.shape[0] > 0
        
        self.sensor = sensor
        self.start_time = int(data[0,0])
        self.end_time = int(data[-1,0])
        self.n_entries = data.shape[0]
        data[:,1] *= 1000.
        self.data_bz2 = bz2.compress(array_to_str(data))

    @property
    def data(self):
        d = np.load( cStringIO.StringIO(bz2.decompress(self.data_bz2)))
        d[:,1] /= 1000.
        return d

    def __repr__(self):
        return '<Recording Array: %d to %d containing %d recordings>' % (self.start_time, self.end_time, self.n_entries)
        
        
    


class ErrorRecording(Base):
    __tablename__ = 'recordingerrors'

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    sensor = relationship("Sensor", backref=backref('errors', order_by=time))
    text = Column(String(200))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
#session = Session()

print engine
