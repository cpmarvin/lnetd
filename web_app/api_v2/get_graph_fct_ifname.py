import datetime
import pandas as pd
from influxdb import InfluxDBClient

def get_graph_ifname(hostname,interface,direction):
        INFLUXDB_HOST = '127.0.0.1'
        INFLUXDB_NAME = 'telegraf'
        if direction == 'in':
            direction = 'ifHCInOctets'
        else:
            direction = 'ifHCOutOctets'
        timestamp = datetime.datetime.utcnow().isoformat()
        client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
        queryurl = '''SELECT non_negative_derivative(max(%s), 1s) *8 as bps from 
                      interface_statistics where hostname =~ /%s/ and ifName = '%s' 
                      AND time > now()- 24h and time <now() 
                      GROUP BY time(5m)''' %(direction,hostname,interface)
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_statistics'))
        df = pd.DataFrame(points)
        df1=df.reindex(columns=["time","bps"]).to_csv(index=False)
        return df1
