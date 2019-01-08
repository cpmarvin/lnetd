import pandas as pd
from influxdb import InfluxDBClient



INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)

def get_max_util(hostname,interface,start):
        if interface == 0:
                    return -1
        int(start)
        queryurl = '''SELECT max(non_negative_derivative) from (SELECT non_negative_derivative(max(ifHCOutOctets), 1s) *8 from 
                        interface_statistics where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh 
                        group by time(5m))''' %(hostname,interface,start)
        result = client.query(queryurl)
        #print queryurl
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return -1
        df = pd.DataFrame(points)
        df.columns = ['bps', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        return result
