import datetime
import pandas as pd
from influxdb import InfluxDBClient

def get_graph_ifindex(hostname,interface):
    INFLUXDB_HOST = '127.0.0.1'
    INFLUXDB_NAME = 'telegraf'

    timestamp = datetime.datetime.utcnow().isoformat()
    client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
    queryurl = '''SELECT non_negative_derivative(max(ifHCOutOctets), 1s) *8 as bps from
                        interface_statistics where hostname =~ /%s/ and ifIndex = '%s'
                        AND time > now()- 24h and time <now()  GROUP BY time(5m)''' %(hostname,interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    df = pd.DataFrame(points)
    df1=df.reindex(columns=["time","bps"]).to_dict(orient='records')
    return df1
