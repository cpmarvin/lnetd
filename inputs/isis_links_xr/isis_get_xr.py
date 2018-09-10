import pandas as pd
import re
from get_output import get_output
from snmp_get import *

def get_isis_db(router):
    output_list = get_output(router,'show isis database verbose')
    interface = {}
    line = -1
    #print output_list 
    for i in output_list.splitlines():
        i = i.strip(' ')
        #print i
        if re.match("^Hostname:",i):
            #line = line +1
            #print "----------------------"
            #print "Hostname line : %s" %i
            hostname = i
            #interface[line] = i.strip().split(':')
            #line = line + 1
        elif re.match("^(Metric:)(?=.*[A-Z])(?=.*\w+[.]\d{2}$)",i):
            #print "---new line"
            line = line + 1
            interface[line] = hostname.strip().encode('ascii','ignore').split(':')
            #print "Match neigh line:  %s" %i
            i = i.split(':')[1].replace('IS-Extended','')
            i = " ".join(i.split())
            metric = i.encode('ascii','ignore').split(' ')[0]
            #print "metric : %s" %metric
            neigh = i.encode('ascii','ignore').split(' ')[1]
            #print "neigh : %s" %neigh
            interface[line].append(metric.encode('ascii','ignore'))
            interface[line].append(neigh.encode('ascii','ignore'))
            #line = line +1
        elif re.match("^Interface IP Address:|^Neighbor IP Address:",i):
            #print "interface and Neight lines: %s" %i
            interface[line].append(i.split(':')[1])
            #print interface[line]
    #return interface
    #print interface
    df = pd.DataFrame(interface.values())
    df = df.dropna()
    df = df[[1,2,3,4,5]]
    df[6] = 0
    df[7] = 0
    df.columns = ['source', 'metric', 'target', 'l_ip','r_ip','l_int','r_int']
    df['target'] = df['target'].str.replace('.00','')
    return df  


df4 = get_isis_db('gb-pe11-lon')
df4 = df4.reset_index()
df4['l_ip'] = df4['l_ip'].astype(str)
df4['r_ip'] = df4['r_ip'].astype(str)
df4 = df4.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df4.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df4.l_ip.values.tolist(), df4.r_ip.values.tolist()))])
df4['l_ip_r_ip'] = df4['l_ip_r_ip'].astype(str)

#uncoment this once telegraf and influx is up
df4['l_int'] = df4.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
df4['util'] = df4.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
df4['capacity'] = df4.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
df4['errors'] = df4.apply(lambda row: get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)

"""
#comment below once influxdb and telegraf is up and running
df4['l_int'] = 34
df4['util'] = random.randint(0,2000)
df4['capacity'] = 1000
df4['errors'] = random.randint(0,2000)
"""


df4 = df4.drop(['index'], axis=1)
#df4 = df4[['source', 'target', 'l_ip', 'metric','l_int','r_ip','r_int','l_ip_r_ip','util','capacity']]
print df4

from sqlalchemy import create_engine,text
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df4.to_sql('Links', disk_engine, if_exists='replace')
