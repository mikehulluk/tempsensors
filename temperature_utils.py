
import time
import numpy
import numpy as np



def get_time():
    return int(time.time())



def smooth(x, window_len):
    w = [1.0/window_len]*window_len
    return numpy.convolve(x, w[::-1], 'same')

def smooth_neat(x, window_len):
    t1 = x[:,0]
    x1 = smooth( x[:,1], window_len=window_len)

    r = np.vstack([t1.T,x1.T]).T
    r=r[window_len:-window_len,:]

    return r
