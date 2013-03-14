
import sqlalchemy
import inspect
import os

from sqlalchemy import Column, Integer, String, Float, ForeignKey#, relationship, backref
from sqlalchemy.orm import relationship, backref



# Figure out the databse name, relative to this file:
module_dir = os.path.dirname( os.path.abspath(inspect.stack()[0][1]))
db_file = os.path.join(module_dir, 'temps.sqllite')


engine = sqlalchemy.create_engine('sqlite:///%s'%db_file)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# Classes:
class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    sensor = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    temperature = Column(Float)
    sensor = relationship("Sensor", backref=backref('recordings', order_by=time))

    def __init__(self, sensor, time, temperature):
        self.sensor = sensor
        self.time = time
        self.temperature = temperature

    def __repr__(self):
           return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)



Base.metadata.create_all(engine)

print engine
