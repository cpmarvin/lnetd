import datetime
import pandas as pd
from influxdb import InfluxDBClient

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)

def get_util_interface(hostname,interface,direction):
    try:
        if direction == 'in':
            direction = 'ifHCInOctets'
        else:
            direction = 'ifHCOutOctets'
        timestamp = datetime.datetime.utcnow().isoformat()
        queryurl = '''SELECT non_negative_derivative(last(%s), 1s) *8 from interface_statistics
                          where hostname =~ /%s/ and ifName = '%s' AND time >= now()- 10m and time <=now()
                          GROUP BY time(5m)''' % (direction,hostname,interface)
        result = client.query(queryurl)
        #print(queryurl,result)
        points = list(result.get_points(measurement='interface_statistics'))
        df = pd.DataFrame(points)
        df.columns = ['bps', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        return result
    except Exception as e:
        return -1
def get_capacity_ifname(hostname,interface,start):
    try:
        if interface == 0 or interface == -1:
            return -1
        int(start)
        client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
        queryurl = '''SELECT last(ifHighSpeed) from interface_statistics 
                where hostname =~ /%s/ and  ifName= '%s' ''' %(hostname,interface)
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return -1
        df = pd.DataFrame(points)
        df.columns = ['capacity', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['capacity']))
        return result
    except Exception as e:
        return -1 
