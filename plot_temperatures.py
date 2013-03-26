


import sys
import os
import time
import numpy as np

#import temperature_db
import temperature_db as tdb
session = tdb.Session()

sensors = session.query(tdb.Sensor).all()


import matplotlib
matplotlib.use('gtkagg')
import pylab
f = pylab.figure()
ax = f.add_subplot(111)
ax2 = ax.twinx()

hist_colors = []
hist_data = []
for sensor in sensors:
    print sensor
    recs = sensor.raw_recordings
    l = np.array([ (r.time, r.temperature) for r in recs])
    print l.shape

    lp = ax.plot(l[:,0], l[:,1],'x-', label='%s' % sensor.address)

    # Errors
    errs = sensor.errors
    err_arr = np.array([ (e.time) for e in errs])
    ax2.plot( err_arr, np.ones_like(err_arr),  'o', color=lp[0].get_color())
    
    hist_data.append(err_arr)
    hist_colors.append(lp[0].get_color())
    
    #ax2.hist( err_arr, bins=20, rwidth=0.1, color=lp[0].get_color())



density=False
nbins = 30
hist1, bin_edges = np.histogram(hist_data[0], density=density, bins=nbins)
hist2, bin_edges = np.histogram(hist_data[1], density=density, bins=bin_edges)
hist3, bin_edges = np.histogram(hist_data[2], density=density, bins=bin_edges)
hist4, bin_edges = np.histogram(hist_data[3], density=density, bins=bin_edges)


width = (bin_edges[1] - bin_edges[0]) / 4.

ax2.bar(bin_edges[:-1] + width*0, hist1, color=hist_colors[0], width=width )#,ls='step', fillstyle='full', alpha=0.2)
ax2.bar(bin_edges[:-1] + width*1, hist2, color=hist_colors[1], width=width )
ax2.bar(bin_edges[:-1] + width*2, hist3, color=hist_colors[2], width=width )
ax2.bar(bin_edges[:-1] + width*3, hist4, color=hist_colors[3], width=width )


#ax2.step(bin_edges[:-1], hist2, color=hist_colors[1])
#ax2.step(bin_edges[:-1], hist3, color=hist_colors[2])
#ax2.step(bin_edges[:-1], hist4, color=hist_colors[3])
ax2.set_ylim( (0,30))

 
ax.legend() 
pylab.show()
