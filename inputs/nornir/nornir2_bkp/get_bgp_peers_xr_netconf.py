import datetime

from netaddr import IPNetwork, IPAddress

from ncclient import manager
from ncclient.xml_ import *
from lxml import etree, objectify
from lxml import etree as ETREE
import ipaddress
import sqlite3

from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, napalm_get, napalm_configure
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import commands
from nornir.core.filter import F

import logging
import sys
#
from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine, text


def get_ix_name(ip,version,ix_lans):
    default = {'name': 'n/a', 'ipv4': 'n/a', 'ipv6': 'n/a'}
    try:
        for i in ix_lans:
            if version == 4:
               	if IPAddress(ip) in IPNetwork(i['ipv4']):
                    return i
            elif version == 6:
               	if IPAddress(ip) in IPNetwork(i['ipv6']):
                    return i
        else:
            return default
    except Exception as e:
        print('error',e)
        return default

def get_lnetd_our_ans():
    """
    Get LnetD ASN configuration
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_config = pd.read_sql("SELECT * FROM App_config", conn)
        return int(df_config['asn'].values[0])
    except:
        return -1

def get_lnetd_bgp_peering_points():
    """
    get LnetD Peering Points
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_links = pd.read_sql("SELECT * FROM Bgp_peering_points", conn)
        df_links = df_links.drop(['index'], axis=1)
        return df_links.to_dict(orient='records')
    except Exception as e:
        print(e)
        return {}
def get_lnetd_bgp_customers():
    """
    get LnetD BGP customers
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_links = pd.read_sql("SELECT * FROM Bgp_customers", conn)
        df_cst = df_links['ASN'].map(lambda x: x.split()[0])
        return df_cst.unique().tolist()
    except:
        return []

def remove_ns(xml_string):
    '''Remove namespace from xml string'''
    xml_string = xml_string.encode('utf-8')
    parser = etree.XMLParser(remove_blank_text=True,encoding='utf-8')
    tree = etree.fromstring(xml_string, parser)
    root = tree.getroottree()

    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'):
            continue  # (1)
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i + 1:]
    objectify.deannotate(root, cleanup_namespaces=True)
    #return(etree.tostring(root, pretty_print=True))
    return(root)

def parse_bgp_xml(result_tree,rtr):
    all_neigh = []
    for isis_id in result_tree.iter('neighbor'):
        #print(isis_id,isis_id[0].text)
        this_neighbor = {}
        this_neighbor['router'] = rtr
        this_neighbor["neighbor_address"]  = isis_id.xpath(".//neighbor-address")[0].text
        try:
            this_neighbor["description"]  = isis_id.xpath(".//description")[0].text
        except :
            this_neighbor["description"] = "NO_DESC"

        #this_neighbor["local_as"] = isis_id.xpath(".//local-as")[0].text
        this_neighbor["remote_as"] =  isis_id.xpath(".//remote-as")[0].text
        this_neighbor["is_up"] = isis_id.xpath(".//connection-state")[0].text
        if this_neighbor["is_up"] =='bgp-st-estab':
            this_neighbor["is_up"] = 1
            uptime = isis_id.xpath(".//connection-established-time")[0].text
            this_neighbor["uptime"] = datetime.timedelta(seconds=int(uptime))
        else:
            this_neighbor["is_up"] = 0
            this_neighbor["uptime"] = 0
        for isis_id2 in isis_id.iter('af-data'):
            #print(isis_id2.xpath(".//af-name")[0].text)
            #print(isis_id2.xpath(".//prefixes-accepted")[0].text)
            family_name = isis_id2.xpath(".//af-name")[0].text
            prefixes = isis_id2.xpath(".//prefixes-accepted")[0].text
            this_neighbor[family_name] = prefixes
        #this_neighbor["uptime"] = 'N/A'
        all_neigh.insert(0,this_neighbor)
    return all_neigh

def get_netconf_xr(task):
    rpc_get_bgp ="""
<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <filter>
    <bgp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-bgp-oper">
      <instances>
        <instance>
          <instance-active>
            <default-vrf>
              <neighbors>
                <neighbor>
                  <description/>
                  <local-as/>
                  <remote-as/>
                  <connection-state/>
                  <connection-established-time/>
                  <neighbor-address/>
                  <af-data>
                    <af-name/>
                    <prefixes-accepted/>
                    </af-data>
                </neighbor>
              </neighbors>
            </default-vrf>
          </instance-active>
          <instance-name/>
        </instance>
      </instances>
    </bgp>
  </filter>
</get>
"""
    hostname = task.host.name
    hostip = task.host.hostname
    username = task.host.username
    password = task.host.password
    try:
        dev = manager.connect(host=hostip,
                             username=username,
                             password=password,
                             hostkey_verify=False,
                             device_params={'name': 'iosxr'},
                             timeout=320)
        res = dev.dispatch(to_ele(rpc_get_bgp))
        res = to_xml(res.data)
        xml_result = remove_ns(res)
        final = parse_bgp_xml(xml_result,hostname)
        return final
    except Exception as e:
      print('Failed',e)
      raise Exception


nr = InitNornir(config_file="config.yaml",dry_run=False)

all_devices = nr.filter(F(groups__contains="peering"))

r = all_devices.run(task=get_netconf_xr)

final_panda = []

for i in r:
    if i in r.failed_hosts.keys():
        print('Fail node',i)
        continue
    else:
        #print(r[i][0].result)
        final_panda = final_panda + r[i][0].result

ix_lans = get_lnetd_bgp_peering_points()
ipt_cst = get_lnetd_bgp_customers()
our_asn = get_lnetd_our_ans()

print('Our ASN',our_asn)

print(ix_lans)

for n in final_panda:
    n['version']  = ipaddress.ip_address(n['neighbor_address']).version

    if n['remote_as'] == str(our_asn):
        n['type'] = 'internal'
        n['ix_name'] = 'n/a'
    else:
        n['type'] = 'peering'
        entry = get_ix_name(n['neighbor_address'], n['version'],ix_lans)
        n['ix_name'] = entry['name']

    if n['version'] == 4:
        if n['uptime'] ==0:
            n['accepted_prefixes'] = 0
        else:
            n['accepted_prefixes'] = n['ipv4']
    else:
       if n['uptime'] ==0:
           n['accepted_prefixes'] = 0
       else:
           n['accepted_prefixes'] = n['ipv6']

df = pd.DataFrame(final_panda)
df = df.loc[:, df.columns.isin(['accepted_prefixes','description','is_up','ix_name','neighbor_address','remote_as','router','uptime','version','type'])]
df = df.rename(columns={'description': 'neighbour', 'neighbor_address': 'neighbour_ip'})

df['uptime'] = df['uptime'].values.astype("timedelta64[m]")
df['uptime'] = df['uptime'].astype(str)
df['uptime'] = df['uptime'].map(lambda x: x[:-10])

print('\nthis is the panda before writing to db\n',df)

disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df.to_sql('Bgp_peers', disk_engine, if_exists='replace')
