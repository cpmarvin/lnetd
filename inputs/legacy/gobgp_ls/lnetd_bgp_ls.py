from __future__ import print_function
from __future__ import unicode_literals

from builtins import str
import grpc
from google.protobuf.any_pb2 import Any
import gobgp_pb2
import gobgp_pb2_grpc
import attribute_pb2
import sys
import socket
import ipaddress
import re
from functools import cmp_to_key
import pandas as pd
from sqlalchemy import create_engine

_AF_NAME = dict()
_AF_NAME[4] = gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
_AF_NAME[6] = gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP6, safi=gobgp_pb2.Family.SAFI_UNICAST)
_AF_NAME["LS"] = gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_LS, safi=gobgp_pb2.Family.SAFI_LS)

_TT = dict()
_TT['global'] = gobgp_pb2.GLOBAL
_TT['in'] = gobgp_pb2.ADJ_IN
_TT['out'] = gobgp_pb2.ADJ_OUT



lnetd_links = []
lnetd_routers = []
import socket

def get_hostname(ip):
  '''Return RDNS entry for router id,
  this is needed as not all bgp-ls implementation support 
  Node Name TLV sect 3.3.1.3.  Node Name TLV #rfc7752
  '''
  ip = str(ip)
  try:
      name = socket.gethostbyaddr(ip)[0]
  except Exception as e:
      name = ip
  return name
def parse_node_messages(nlri,path):
  '''Parse node and nlri messages , update lnetd list ,
  need to find another way here'''
  nn_cls = getattr(attribute_pb2, 'LsNodeNLRI', None)
  #print(nn_cls)
  #print(nlri)
  if nn_cls:
      pattr_obj = nn_cls()
      nlri.nlri.Unpack(pattr_obj)
      for k in pb_msg_attrs(pattr_obj):
          if k == "local_node":
              local_node = pattr_obj.local_node.igp_router_id
          else:
              print('Invalid BGP-LS Node Update')
              sys.exit()
      entry_node = {"igp_router_id":local_node}
  for attr_name in pb_msg_attrs(path):
      if attr_name == "nlri":
          continue
      if attr_name == "pattrs":
          for pattr in path.pattrs:
              pattr_name = pattr.type_url.split(".")[-1]
              pattr_cls = getattr(attribute_pb2, pattr_name, None)
              if pattr_cls:
                  pattr_obj = pattr_cls()
                  pattr.Unpack(pattr_obj)
              for k in pb_msg_attrs(pattr_obj):
                  if k =="node":
                      v = str(getattr(pattr_obj, k, "")).strip().replace("\n", ", ")
                      entry_node['local_router_id'] = pattr_obj.node.local_router_id
                      entry_node['name'] = get_hostname( entry_node['local_router_id'] )
  lnetd_routers.append(entry_node)  
def parse_link_messages(nlri,path):
  '''Parse path and nlri messages , update lnetd list ,
  need to find another way here'''
  nn_cls = getattr(attribute_pb2, 'LsLinkNLRI', None)
  #print(path)
  if nn_cls:
      pattr_obj = nn_cls()
      nlri.nlri.Unpack(pattr_obj)
      for k in pb_msg_attrs(pattr_obj):
          if k == "local_node":
              local_node = pattr_obj.local_node.igp_router_id
          elif k == "remote_node":
              remove_node = pattr_obj.remote_node.igp_router_id
          elif k =="link_descriptor":
              l_ip = pattr_obj.link_descriptor.interface_addr_ipv4
              r_ip = pattr_obj.link_descriptor.neighbor_addr_ipv4
          else:
              print('Invalid BGP-LS Link Update')
              sys.exit()
      #print(local_node,l_ip,remove_node,r_ip)
      entry = {"source":local_node,"target":remove_node,"l_ip":l_ip,"r_ip":r_ip}
  for attr_name in pb_msg_attrs(path):
      if attr_name == "nlri":
          continue
      if attr_name == "pattrs":
          for pattr in path.pattrs:
              pattr_name = pattr.type_url.split(".")[-1]
              pattr_cls = getattr(attribute_pb2, pattr_name, None)
              if pattr_cls:
                  pattr_obj = pattr_cls()
                  pattr.Unpack(pattr_obj)
              for k in pb_msg_attrs(pattr_obj):
                  if k == "link":
                      metric = pattr_obj.link.igp_metric
                      entry["metric"] = metric
  lnetd_links.append(entry)

def pb_msg_attrs(m):
  # return list of attr names
  slice_ind = -1 * len('_FIELD_NUMBER')
  attrs = [ attr[:slice_ind].lower() for attr in dir(m) if attr.endswith('_FIELD_NUMBER') ]
  if attrs:
    return attrs
  # temporary workaround for an issue with python3 generated message classes that include no field number constants.
  return [ attr for attr in dir(m) if re.match(r'[a-z]', attr) ]

def print_path(path):
  nlri = attribute_pb2.LsAddrPrefix()
  path.nlri.Unpack(nlri)
  #print(path)
  if nlri.type == 2:
    '''This is Link Message type'''
    parse_link_messages(nlri,path)
  elif nlri.type == 1:
    '''This is the Node Message type'''
    parse_node_messages(nlri,path)
  elif nlri.type == 3:
    '''TODO'''
    return {}
  else:
      return {}

def run(gobgpd_addr, timeout):
  # family
  family = _AF_NAME['LS']
  table_type = _TT["global"]
  name = None    
  channel = grpc.insecure_channel(gobgpd_addr + ":50051")
  stub = gobgp_pb2_grpc.GobgpApiStub(channel)
  res = stub.ListPath(
          gobgp_pb2.ListPathRequest(
            table_type=table_type,
            name=name,
            family=family,
            ),
          timeout,
          )
  destinations = [ d for d in res ]
  for p in [ p for d in destinations for p in d.destination.paths ]:
    print_path(p)

  #print('this is the final lnetd_links')
  '''
  Links format 
  [{'source': '0002.0020.0200', 'target': '0003.0030.0300', 'l_ip': '10.22.33.22', 'r_ip': '10.22.33.33', 'metric': 10}]
  '''
  #print(lnetd_links)
  print('\nthis is the final routers\n')
  '''
  Router Format
  [{'igp_router_id': '0007.0070.0700', 'local_router_id': '10.7.7.7', 'name': 'fr-p7-mrs'}]
  '''
  #print(lnetd_routers)
  #generate nsap_ip name mapping

  map_nsap = {}
  for entry in lnetd_routers:
      map_nsap[entry['igp_router_id']] = entry['name']
  
  df_links = pd.DataFrame(lnetd_links)
  df_links['source'] = df_links.apply(lambda row: map_nsap[row['source']],axis=1)
  df_links['target'] = df_links.apply(lambda row: map_nsap[row['target']],axis=1)
  df_links.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(
        zip(df_links.l_ip.values.tolist(), df_links.r_ip.values.tolist()))])
  df_links['l_ip_r_ip'] = df_links['l_ip_r_ip'].astype(str)
  print('\nThis is the final lnetd_links ... writing to db now \n',df_links)
  try:
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df_links.to_sql('rpc_links', disk_engine, if_exists='replace')
  except Exception as e:
    print(e)
  
  #generate final routers
  df_routers = pd.DataFrame(lnetd_routers)
  df_routers = df_routers.drop(['igp_router_id'], axis=1)
  df_routers = df_routers.rename(columns={'local_router_id': 'ip'})
  df_routers.loc[:, 'country'] = df_routers['name'].str[0:2]
  df_routers = df_routers.fillna(0)
  print('\nThis is the final lnetd_routers ... writing to db now \n',df_routers)
  try:
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df_routers.to_sql('rpc_routers', disk_engine, if_exists='replace')
  except Exception as e:
    print(e)

def main():
  gobgpd_addr = "127.0.0.1"
  timeout = 10
  run(gobgpd_addr,
      timeout,
      )

if __name__ == '__main__':
  main()
