

import pylab

from datastore import SensorDataWriter, DataConsolidator




def do_plot(args):
    data = DataConsolidator()
    df = data.extract_dataframe('1H')
    df = data.extract_dataframe('1H')
    df.plot()

    pylab.show()



def main():
    do_plot(None)



if __name__=='__main__':
    main()
