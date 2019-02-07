import pandas as pd
from sqlalchemy import create_engine,text
import sqlite3
import pandas as pd
from sqlalchemy import create_engine,text


disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')

def get_hosname(ip):
    sql_qry = "select name from Routers where ip = '%s'" %(ip)
    router_name = disk_engine.execute(text(sql_qry).execution_options(autocommit=True))
    router = router_name.fetchall()
    if not router:
        return -1
    else:
        return str(router[0][0])

def get_demand_netflow():
    try:
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/pmacct.db")
        #create pandas frame
        sql='''SELECT peer_ip_src,peer_ip_dst,bytes FROM acct_bgp '''
        df_netflow=pd.read_sql(sql, conn)
        df_netflow['bps'] = df_netflow.apply(lambda row: row['bytes'] * 8 / 300,axis=1)
        df_netflow['source'] = df_netflow.apply(lambda row: get_hosname(row['peer_ip_src']),axis=1)
        df_netflow['target'] = df_netflow.apply(lambda row: get_hosname(row['peer_ip_dst']),axis=1)
        df_netflow=df_netflow[df_netflow['target'].str.contains("-1") == False]
        df_netflow = df_netflow.drop(['peer_ip_src', 'peer_ip_dst', 'bytes'], axis=1)
        df_netflow.columns = ['demand','source','target']
        #print df_netflow
        return df_netflow.to_dict(orient='records')
    except Exception,e:
       print 'something went wrong here: {}'.format(e)
       return [{}]
