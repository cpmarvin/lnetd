import datetime
import pandas as pd
from influxdb import InfluxDBClient

def get_interface_ifName(hostname,interface):
	INFLUXDB_HOST = '127.0.0.1'
	INFLUXDB_NAME = 'telegraf'
	timestamp = datetime.datetime.utcnow().isoformat()
	client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
	queryurl = "show tag values with key = ifName where hostname =~ /%s/ and ifIndex ='%s'" %(hostname,interface)
	result = client.query(queryurl)
	points = list(result.get_points(measurement='interface_statistics'))
	df = pd.DataFrame(points)
	df.columns = ['Ifindex', 'IfName']
	df1=df.to_dict(orient='records')
	return str(df1[0]['IfName'])


