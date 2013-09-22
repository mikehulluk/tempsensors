
import numpy
import numpy as np

def do_importfromv1(arg):

    print 'Importing Data from file:'


    from old.temperature_db import *
    
    all_data = np.empty( (0,3) )
    session = Session()
    for i,sensor in enumerate( session.query(Sensor) ):
        print sensor
        
        sensor_data = sensor.get_np_array(session=session)
        print sensor_data.shape
        

        sensor_data = numpy.hstack( (sensor_data, np.ones( (sensor_data.shape[0],1)) * (sensor.id) ) )
        #sensor_data = sensor_data.view( ('f8') 
        print sensor_data[:10,:]
        
        print sensor_data.dtype
        print sensor_data.shape
        print all_data.shape
        
        all_data = np.vstack( (all_data, sensor_data) )
        
        if i>3:
            break
        
    
    #all_data = all_data.view('i32','f32','i8')
    print 'Building Structured array'
    all_data = np.core.records.fromarrays([all_data[:,0],all_data[:,1],all_data[:,2]],names='f0,f1,f2')
    print 'Sorting'
    all_data.sort( axis=0, order=['f0','f1'] )
    
    print all_data.shape
    print all_data[:100]
    
    
    
    raise NotImplementedError()
