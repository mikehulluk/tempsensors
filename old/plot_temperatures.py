


import sys
import os
import time
import numpy as np
import matplotlib.dates as md
import datetime
from matplotlib import dates

#import temperature_db
import temperature_db as tdb
import temperature_utils as utils
session = tdb.Session()

sensors = session.query(tdb.Sensor).all()


import matplotlib
matplotlib.use('gtkagg')
import pylab
import pylab as plt

f = pylab.figure()
ax = f.add_subplot(111)

plt.subplots_adjust(bottom=0.2)
plt.xticks( rotation=25 )


hist_colors = []
hist_data = []

ax.xaxis_date()
xloc = dates.AutoDateLocator()
ax.xaxis.set_major_locator(xloc)
#xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
xfmt = md.AutoDateFormatter(locator=xloc)
ax.xaxis.set_major_formatter(xfmt) 


for sensor in sensors:
    print sensor
    d = sensor.get_np_array(session=session, dates_to_mpl=True)

    lp = ax.plot(d[:,0], d[:,1],'x-',  alpha=0.3)

    window_length = 151
    lsmooth = utils.smooth_neat(d, window_len=window_length)
    lp = ax.plot(lsmooth[:,0], lsmooth[:,1],'-', label='%s' % sensor.address, color=lp[0].get_color(), lw=3 )

    # Errors
    #errs = sensor.errors
    #err_arr = np.array([ (e.time) for e in errs])
    #ax2.plot( err_arr, np.ones_like(err_arr),  'o', color=lp[0].get_color())
    
    #hist_data.append(err_arr)
    #hist_colors.append(lp[0].get_color())

    #break
    



#include_errors = False
#if include_errors:
#    density=False
#    nbins = 30
#    hist1, bin_edges = np.histogram(hist_data[0], density=density, bins=nbins)
#    hist2, bin_edges = np.histogram(hist_data[1], density=density, bins=bin_edges)
#    hist3, bin_edges = np.histogram(hist_data[2], density=density, bins=bin_edges)
#    hist4, bin_edges = np.histogram(hist_data[3], density=density, bins=bin_edges)
#
#
#    width = (bin_edges[1] - bin_edges[0]) / 4.
#
#    ax2.bar(bin_edges[:-1] + width*0, hist1, color=hist_colors[0], width=width )#,ls='step', fillstyle='full', alpha=0.2)
#    ax2.bar(bin_edges[:-1] + width*1, hist2, color=hist_colors[1], width=width )
#    ax2.bar(bin_edges[:-1] + width*2, hist3, color=hist_colors[2], width=width )
#    ax2.bar(bin_edges[:-1] + width*3, hist4, color=hist_colors[3], width=width )
#
#
#    #ax2.step(bin_edges[:-1], hist2, color=hist_colors[1])
#    #ax2.step(bin_edges[:-1], hist3, color=hist_colors[2])
#    #ax2.step(bin_edges[:-1], hist4, color=hist_colors[3])
#    ax2.set_ylim( (0,30))
#ax.legend() 
ax.grid('on')
pylab.show()
