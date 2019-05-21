from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result

import pandas as pd
import re
import sqlite3
import numpy as np
import time
import math

import concurrent.futures
from sqlalchemy import create_engine, text


def write_sql(df):
    try:
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df.to_sql('Links_latency', disk_engine, if_exists='replace')
        add_to_table = disk_engine.execute(text("insert into Links_latency_time select null,*,DATETIME('now') from Links_latency").
                                           execution_options(autocommit=True))
        delete_old_values = disk_engine.execute(text("DELETE FROM Links_latency_time WHERE timestamp <= date('now','-12 day')").
                                                execution_options(autocommit=True))
    except Exception as e:
        print(e)


def get_lnetd_links():
    # get links into panda filter by core only devices
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    df_links = pd.read_sql("SELECT * FROM Links ", conn)
    df_links = df_links[df_links['r_ip'] != '0']
    #df_links = df_links[df_links['capacity'] != -1]
    #regex_pat = re.compile(r'^L.+-P[1-9,E,R].+', flags=re.IGNORECASE)
    #df_links = df_links[df_links['source'].str.match(regex_pat)]
    #df_links = df_links[df_links['target'].str.match(regex_pat)]
    df_links = df_links.drop(['index'], axis=1)
    return df_links


def parse_output(output, pattern_res):
    # parse output and return the maximum latency
    output_clean = ' '.join(output.split())
    output_list = output.splitlines()
    #print('output_list is :',output_list)
    pattern = re.compile(r'\bround-trip\b', flags=re.I)
    for i in output_list:
        # print('line', i)
        if pattern.findall(i):
            # print('pattern', i)
            summary = re.findall(pattern_res, i)[0]
            summary = summary.split('/')
            #print('this is the summary',summary)
            maximum = math.ceil(float(summary[1]))
            #print('maximum', maximum)
            break
        else:
            maximum = 0
    return maximum


def collect_ping_results(task, remote_ip):
    # collect ping result based on platform
    print(f'this is {task.host.name} with {remote_ip} running {task.host.platform}')
    if task.host.platform == 'junos':
        command_req = f'ping {remote_ip} count 5 rapid'
        pattern_res = r'min/avg/max.+ = (\S+)'
    # print(command_req)
    task.host.open_connection("netmiko", configuration=task.nornir.config)
    for ip_address in remote_ip:
        command_req = f'ping {ip_address}'
        pattern_res = r'min/avg/max = (\S+)'
        if task.host.platform == 'junos':
            command_req = f'ping {ip_address} count 5 rapid'
            pattern_res = r'min/avg/max.+ = (\S+)'
        print('command_req is: on host:', command_req, task.host.name)
        r = task.run(task=netmiko_send_command, command_string=command_req,
                     delay_factor=10)
        # print_result(r)
        # create result dict and add it to the global variable
        latency_dict = {}
        latency_dict['source'] = task.host.name
        latency_dict['r_ip'] = ip_address
        latency_dict['latency'] = parse_output(r.result, pattern_res)
        latency_db.insert(0, latency_dict)
        #print('this is the latency_db', latency_db)
    task.host.close_connection("netmiko")
    # return latency_dict


def collect_latency(device, remote_ip):
    # helper function to pass this to nornir
    print("collect_latency function")
    rtr = nr.filter(name=device)
    r = rtr.run(task=collect_ping_results, remote_ip=remote_ip)


latency_db = []
nr = InitNornir(config_file="config.yaml")
df = get_lnetd_links()


def helper_function(device):
    # helper function for concurent
    ip_list = df['r_ip'].loc[df['source'] == device].tolist()
    collect_latency(device, ip_list)
    return latency_db


# create the process pool based on uniq hosts as nr of processes
with concurrent.futures.ProcessPoolExecutor(df['source'].unique().size) as executor:
    # submit jobs to the pool.
    futures = [executor.submit(helper_function, device) for device in df['source'].unique()]
    # As futures are completed they are returned and the result can be
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        #print(i, future.result())
        #print('latency_db', latency_db)
        latency_db.insert(0, future.result())

# flat list into final list
flat_list = []
for i in latency_db:
    for n in i:
        flat_list.append(n)

# create df_latency from list
df_latency = pd.DataFrame(flat_list)

# merge existing links panda with latency
m = df.merge(df_latency, on=['source', 'r_ip'], how='outer', suffixes=['', '_current'], indicator=True)
# take only the required fields
df_latency_final = m[['source', 'target', 'metric', 'l_ip', 'l_int', 'r_ip', 'l_ip_r_ip', 'util', 'capacity', 'latency','errors']]
# fill NA with -1 , because some routers will fail
df_latency_final = df_latency_final.fillna(-1)
print(df_latency_final)
# write to db
write_sql(df_latency_final)

