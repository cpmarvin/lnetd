from mutils import get_netconf
from mutils import parse_xml,write_to_db
import pandas as pd

import logging

import sys
sys.path.append('../utils/')
from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'DEBUG')

rpc_hostname = """
<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <filter>
    <isis xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-clns-isis-oper">
      <instances>
        <instance>
          <host-names>
            <host-name>
              <host-name/>
              <system-id/>
            </host-name>
          </host-names>
          <instance-name/>
        </instance>
      </instances>
    </isis>
  </filter>
</get>
"""
rpc_mpls = """
<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <filter>
    <mpls-te xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-mpls-te-oper">
      <topology-briefs/>
    </mpls-te>
  </filter>
</get>
"""

def main():
    logger.info('Get Netconf data')    
    mpls_te, isis_hostname = get_netconf(rpc_mpls,rpc_hostname)
    #print(mpls_te)
    logger.info('Parse xml data for hostname')
    df_hostname = parse_xml('hostname', isis_hostname)
    logger.info('Parse xml data for links')
    df_links = parse_xml('links', mpls_te)
    df_links['source'] = df_links.apply(lambda row: df_hostname[row['source']], axis=1)
    df_links['target'] = df_links.apply(lambda row: df_hostname[row['target']], axis=1)
    df_links.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df_links.l_ip.values.tolist(), df_links.r_ip.values.tolist()))])
    df_links['l_ip_r_ip'] = df_links['l_ip_r_ip'].astype(str)
    print(df_links)
    df_routers = parse_xml('routers', mpls_te)
    df_routers['name'] = df_routers.apply(lambda row: df_hostname[row['name']], axis=1)
    df_routers.loc[:, 'country'] = df_routers['name'].str[0:2]
    #print(df_routers)
    # write to db
    logger.info('Write to Database')
    write_to_db('rpc_routers',df_routers)
    write_to_db('rpc_links',df_links)


if __name__ == '__main__':
    main()

