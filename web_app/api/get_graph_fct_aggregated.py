import datetime
import pandas as pd
from influxdb import InfluxDBClient

def get_graph_aggregated(source,target):
	INFLUXDB_HOST = '127.0.0.1'
	INFLUXDB_NAME = 'telegraf_agg'

	timestamp = datetime.datetime.utcnow().isoformat()
	client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
	queryurl = '''SELECT sum(bps_out) as bps from 
                      h_interface_statistics where source =~ /%s/ and target =~ /%s/ 
                      AND time > now()- 7d GROUP BY time(1h)''' %(source,target) 
	result = client.query(queryurl)
	points = list(result.get_points(measurement='h_interface_statistics'))
	df = pd.DataFrame(points)
	df.columns = ['bps', 'time']
	df1=df.reindex(columns=["time","bps"]).to_csv(index=False)
	return df1

