
import temperature_utils

import temperature_db as tdb
import numpy as np




seconds_per_block =  1 * 60



def get_block_start_time(t):
    return (t // seconds_per_block) * seconds_per_block


time_s = temperature_utils.get_time()
current_block_start = get_block_start_time(time_s) #(time_s // seconds_per_block) * seconds_per_block



print 'Time now:', time_s
print 'Current block start', current_block_start
print 'Time into current block:', time_s - current_block_start




def _consolidate_sensor(sensor, session):
   
    # Look for old items:
    
    old_recs = session.query(tdb.RawRecording)\
                        .filter( tdb.RawRecording.sensor_id == sensor.id )\
                        .filter( tdb.RawRecording.time < current_block_start )\
                        .order_by('time')
    
    
    if old_recs.count() == 0:
        return False
                    
    oldest_rec= old_recs[-1]                
    
    
    #Pack down the old block:
    old_block_starttime = get_block_start_time(int(oldest_rec.time))
    old_block_endtime = old_block_starttime + seconds_per_block
        
    recs = session.query(tdb.RawRecording).filter( 
                tdb.RawRecording.sensor_id == sensor.id, 
                tdb.RawRecording.time >= old_block_starttime,
                tdb.RawRecording.time < old_block_endtime,
                ).order_by('time').all()
    
    print 'Found %d  between: %d and  %d '% ( len(recs), old_block_starttime, old_block_endtime)
    
    data= np.array([(0,0)] + [ (int(rec.time), int(rec.temperature*1000)) for rec in recs])
    
    
    ra = tdb.RecordingArray(sensor=sensor, data=data)
    session.add(ra)
    for rec in recs:
        session.delete(rec)
    session.commit()
    return True
    
    




def consolidate_sensor(sensor, session):
    print 'Sensor', sensor
    
    while _consolidate_sensor(sensor, session):
        pass
    print ' -- Finshed'
    

def main():

    print 'Consolidating DB'
    print 'Packing into %ds blocks'% seconds_per_block


    import temperature_db
    session = temperature_db.Session()

    
    for sensor in session.query(temperature_db.Sensor).all():
        consolidate_sensor(sensor, session)


if __name__=='__main__':
    main()
