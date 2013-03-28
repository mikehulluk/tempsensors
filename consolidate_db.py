
import temperature_utils

import temperature_db as tdb
import numpy as np
import os


 # Use 24-hr blocks:
seconds_per_block =  60 * 60 * 24

def get_block_start_time(t):
    return (t // seconds_per_block) * seconds_per_block






def _consolidate_sensor(sensor, session, current_block_start):

    # Look for old items:
    old_recs = sensor.Q_raw_recordings_in_range(session=session, end=current_block_start)

    if old_recs.count() == 0:
        return False

    oldest_rec= old_recs[-1]


    #Pack down the old block:
    old_block_starttime = get_block_start_time(int(oldest_rec.time))
    old_block_endtime = old_block_starttime + seconds_per_block

    recs = sensor.Q_raw_recordings_in_range(
                session=session,
                start=old_block_starttime, 
                end=old_block_endtime).all()
    assert len(recs) > 0

    msg = '  -- Found %d  between: %d and  %d '% ( len(recs), old_block_starttime, old_block_endtime)
    print msg,

    data= np.array( [ (rec.time, rec.temperature) for rec in recs])


    ra = tdb.RecordingArray(sensor=sensor, data=data)
    session.add(ra)
    for rec in recs:
        session.delete(rec)
    session.commit()

    print '(BZ2 size: %d Bytes)' % len(ra.data_bz2)
    return True






def consolidate_sensor(sensor, session, current_block_start):
    print 'Sensor', sensor

    while _consolidate_sensor(sensor, session, current_block_start):
        pass


    print '  -- Finshed (%d outstanding)' % len (sensor.raw_recordings)

import temperature_db

def consolidate_db(session):

    time_s = temperature_utils.get_time()
    current_block_start = get_block_start_time(time_s)

    print 'Time now:', time_s
    print 'Current block start', current_block_start
    print 'Time into current block:', time_s - current_block_start

    print 'Consolidating DB'
    print 'Packing into %ds blocks'% seconds_per_block

    original_db_size = os.path.getsize(tdb.db_file)



    for sensor in session.query(temperature_db.Sensor).all():
        consolidate_sensor(sensor, session, current_block_start)
    session.commit()


    # Vacuuming database:
    print 'Vacuuming database:'
    session.execute('VACUUM')
    session.flush()

    final_db_size = os.path.getsize(tdb.db_file)
    print 'DB Size (kB)(Orig): %.2f'% (original_db_size/1000.)
    print 'DB Size (kB)(Final):%.2f'% (final_db_size/1000.)

def main():
    session = temperature_db.Session()
    consolidate_db(session=session)

if __name__=='__main__':
    main()
