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
        return ip
    else:
        return str(router[0][0])

def get_demand_newtflow(router='none',interface='none'):
    try:
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/pmacct.db")
        #create pandas frame
        sql='''SELECT peer_ip_src,peer_ip_dst,bytes,peer_as_dst FROM
            acct_bgp where peer_ip_src = '%s' and iface_in=%s and bytes >= 187000000 ''' %(router,interface)
        df_netflow=pd.read_sql(sql, conn)
        return df_netflow
    except Exception as e:
        print(e)
        return {}

def return_cc(name):
    if '-' in name:
        return name[:2]
    else:
        return 'NO-NHS'
