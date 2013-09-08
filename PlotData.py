



import pylab

from datastore import SensorDataWriter, DataConsolidator




def main():

    data = DataConsolidator()
    
    df = data.extract_dataframe('1H')

    df.plot()

    pylab.show()



main()
