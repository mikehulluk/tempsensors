
import sqlalchemy
import inspect
import os

from sqlalchemy import Column, Integer, String, Float, ForeignKey#, relationship, backref
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



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


class Recording(Base):
    __tablename__ = 'recordings'

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    temperature = Column(Float)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))

    sensor = relationship("Sensor", backref=backref('recordings', order_by=time))

    def __init__(self, sensor, time, temperature):
        self.sensor = sensor
        self.time = time
        self.temperature = temperature

    def __repr__(self):
           return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)



Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
#session = Session()

print engine
