


s1_src = "/sys/bus/w1/devices/28-000004623b55/w1_slave"



def get_temperature(src):
	with open(s1_src) as s1:
		d = s1.read()
	#print d
	t = d.split('\n')[1].split(" ")[9].split('=')[1]
	return float(t)/1000.

while True:
	
	t1 = get_temperature(s1_src)
	print 'Sensor temperature:', t1
	
	#print t

