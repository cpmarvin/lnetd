import pandas as pd
from sqlalchemy import create_engine, text
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text


disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')


def get_device_names():
    sql_qry = "select name,ip from Routers"
    routers = pd.read_sql("SELECT name,ip FROM Routers ", disk_engine)
    routers_dict = dict(zip(routers['ip'], routers['name']))
    # router_name = disk_engine.execute(text(sql_qry).execution_options(autocommit=True))
    # router = router_name.fetchall()
    if not routers_dict:
        return -1
    else:
        return routers_dict

def map_ip_to_name(routers_dict,ip):
    try:
        rtr_name = routers_dict[ip]
        return rtr_name
    except Exception as e:
        return ip

def get_demand_netflow():
    try:
        #get router names
        routers_dict = get_device_names()
        # connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/pmacct.db")
        # create pandas frame
        sql = '''SELECT peer_ip_src,peer_ip_dst,sum(bytes) as bytes  FROM acct_bgp group by peer_ip_src,peer_ip_dst'''
        #SELECT peer_ip_src,peer_ip_dst,bytes FROM acct_bgp where datetime(stamp_inserted) between  datetime('now','-'||10||' minutes') and datetime('now')"
        df_netflow = pd.read_sql(sql, conn)
        df_netflow['bps'] = df_netflow.apply(lambda row: row['bytes'] * 8 / 300, axis=1)
        df_netflow['source'] = df_netflow.apply(lambda row: map_ip_to_name(routers_dict,row['peer_ip_src']), axis=1)
        df_netflow['target'] = df_netflow.apply(lambda row: map_ip_to_name(routers_dict,row['peer_ip_dst']), axis=1)
        df_netflow = df_netflow[df_netflow['target'].str.contains("-1") == False]
        df_netflow = df_netflow.drop(['peer_ip_src', 'peer_ip_dst', 'bytes'], axis=1)
        df_netflow.columns = ['demand', 'source', 'target']
        # print df_netflow
        return df_netflow.to_dict(orient='records')
    except Exception as e:
        print(e)
        return {}
