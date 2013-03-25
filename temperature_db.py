
import sqlalchemy
import inspect
import os
import numpy as np
import cStringIO
import bz2


from sqlalchemy import Column, Integer, String, Float, Text, LargeBinary, ForeignKey#, relationship, backref
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base




def array_to_str(arr):
    op = cStringIO.StringIO()
    np.save(op, arr)
    return op.getvalue()





# Figure out the databse name, relative to this file:
module_dir = os.path.dirname( os.path.abspath(inspect.stack()[0][1]))
db_file = os.path.join(module_dir, 'temps.sqllite')


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
        
        self.sensor = sensor
        self.start_time = int(data[0,1])
        self.end_time = int(data[-1,1])
        self.n_entries = data.shape[0]
        self.data_bz2 = bz2.compress(array_to_str(data))

        
        
    


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
