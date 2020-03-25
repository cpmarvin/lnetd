import datetime
import pandas as pd
from influxdb import InfluxDBClient
import redis,pickle
import sqlite3

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)


def get_interface_ifName(hostname,interface):
    timestamp = datetime.datetime.utcnow().isoformat()
    client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
    queryurl = "show tag values with key = ifName where hostname =~ /%s/ and ifIndex ='%s'" %(hostname,interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    df = pd.DataFrame(points)
    df.columns = ['Ifindex', 'IfName']
    df1=df.to_dict(orient='records')
    return str(df1[0]['IfName'])

def get_util_interface(hostname, interface, direction):
    try:
        if direction == 'in':
            direction = 'ifHCInOctets'
        else:
            direction = 'ifHCOutOctets'
        timestamp = datetime.datetime.utcnow().isoformat()
        queryurl = '''SELECT non_negative_derivative(last(%s), 1s) *8 as bps from interface_statistics
                          where hostname =~ /%s/ and ifName = '%s' AND time >= now()- 10m and time <=now()
                          GROUP BY time(5m)''' % (direction, hostname, interface)
        result = client.query(queryurl)
        # print(queryurl,result)
        points = list(result.get_points(measurement='interface_statistics'))
        df = pd.DataFrame(points)
        df = df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        return result
    except Exception as e:
        return -1


def get_capacity_ifname(hostname, interface, start):
    try:
        if interface == 0 or interface == -1:
            return -1
        int(start)
        client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)
        queryurl = '''SELECT last(ifHighSpeed) as capacity from interface_statistics
                where hostname =~ /%s/ and  ifName= '%s' ''' % (hostname, interface)
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return -1
        df = pd.DataFrame(points)
        df = df.to_dict(orient='records')
        result = int(round(df[0]['capacity']))
        return result
    except Exception as e:
        return -1

def update_redis(key_name, data, time):
    conn = redis.Redis("localhost")
    redis_data = pickle.dumps(data)
    conn.set(key_name, redis_data)
    conn.expire(key_name, time)


def check_redis(key_name):
    conn = redis.Redis("localhost")
    redis_data = conn.get(key_name)
    if redis_data:
        data = pickle.loads(redis_data)
        return data
    else:
        return {}


def get_alert_backoff():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    sql_app_config = pd.read_sql("select * from App_config", conn)
    alert_thresold = sql_app_config["alert_threshold"].values[0]
    alert_backoff =  sql_app_config["alert_backoff"].values[0]
    alert_backoff_sec = int(alert_backoff) * 60
    return alert_backoff_sec

