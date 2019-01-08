import datetime
import pandas as pd
from influxdb import InfluxDBClient

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)

def get_ifIndex_IP(hostname,interface):
        if interface == 0:
            return -1
        timestamp = datetime.datetime.utcnow().isoformat()
        queryurl = "SELECT Ifindex from interface_address where hostname =~ /%s/ and  index = '%s' ORDER BY DESC limit 1" %(hostname,interface)
	#print queryurl
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_address'))
        if not points:
            return -1
        df = pd.DataFrame(points)
        df.columns = ['ifIndex', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['ifIndex']))
        return result

def get_uti_ifIndex(hostname,interface,start):
        if interface == -1:
            return -1
        int(start)
        timestamp = datetime.datetime.utcnow().isoformat()
        queryurl = "SELECT non_negative_derivative(last(ifHCOutOctets), 1s) *8 from interface_statistics where hostname =~ /%s/ and  ifIndex = '%s' AND time >= now()- %sh10m and time <=now()- %sh GROUP BY time(5m)" %(hostname,interface,start,start)
        #print queryurl
	result = client.query(queryurl)
	#print "results: %s" %result
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return -1

        df = pd.DataFrame(points)
        df.columns = ['bps', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        return result


def get_capacity_ifIndex(hostname,interface):
    if interface == 0 or interface == -1:
        return -1
    client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
    queryurl = "SELECT last(ifHighSpeed) from interface_statistics where hostname =~ /%s/ and  ifIndex = '%s'" %(hostname,interface)
    #print queryurl
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        return -1
    df = pd.DataFrame(points)
    df.columns = ['capacity', 'time']
    df=df.to_dict(orient='records')
    result = int(round(df[0]['capacity']))
    return result

def get_errors_ifIndex(hostname,interface,start):
        if interface == 0:
            return -1
        int(start)
        timestamp = datetime.datetime.utcnow().isoformat()
        queryurl = "SELECT non_negative_derivative(last(ifInErrors), 1s) from interface_statistics where hostname =~ /%s/ and  ifIndex = '%s' AND time >= now()- %sh5m and time <=now()- %sh GROUP BY time(5m)" %(hostname,interface,start,start)
        #print queryurl
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return -1

        df = pd.DataFrame(points)
        df.columns = ['bps', 'time']
        df=df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        return result
