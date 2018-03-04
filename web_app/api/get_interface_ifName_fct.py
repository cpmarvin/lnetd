import datetime
import pandas as pd
from influxdb import InfluxDBClient

def get_interface_ifName(hostname,interface):
	
	INFLUXDB_HOST = '127.0.0.1'
	INFLUXDB_NAME = 'telegraf'
	timestamp = datetime.datetime.utcnow().isoformat()

	client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
	
	queryurl = "show tag values with key = ifName where hostname =~ /%s/ and ifIndex ='%s'" %(hostname,interface)
	print queryurl
	result = client.query(queryurl)
	points = list(result.get_points(measurement='interface_statistics'))
	df = pd.DataFrame(points)
        print df
	df.columns = ['Ifindex', 'IfName']
	df1=df.to_dict(orient='records')
	#df1=df.to_dict(orient='records',double_precision=0)
	return str(df1[0]['IfName'])
	#return "red"

