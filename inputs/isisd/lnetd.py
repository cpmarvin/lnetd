from isis_v02  import *
import threading
import time
import pandas as pd
import networkx as nx
import random
import logging
from sqlalchemy import create_engine 
import sys
import copy
sys.path.append('../utils/')

from snmp_get import * 
from lnetd_log import get_module_logger

config = ConfigParser.ConfigParser()
config.read("./isisd.ini")

logger = get_module_logger(__name__,'DEBUG')
def lnetd_prefixes(new_list):
    prefixes_list = []
    for i in new_list:
        try:
            source = i.data[137][0]['V'][0]
            #print INDENT,'name',i.name
            #print INDENT,'132:',i.data[132]
            for data_135 in i.data[135]:
                for n in data_135['V']:
                    #print 'this is the n:',n
                    #print 'this is the nodes_names',node_names
                    ip = n['prefix']
                    #print ('%s,%s,%s') %(source,target,metric)
                    prefixes = {"name": source,
                                "ip": ip,
                               }
                    #print '-----final_entry :',final_entry
                    prefixes_list.append(prefixes)
            for data_236 in i.data[236]:
                for n in data_236['V']:
                    #print 'this is the n:',n
                    #print 'this is the nodes_names',node_names
                    ip = n['prefix']
                    #print ('%s,%s,%s') %(source,target,metric)
                    prefixes_v6 = {"name": source,
                                "ip": ip,
                               }
                    #print '-----final_entry :',final_entry
                    prefixes_list.append(prefixes_v6)
        except Exception as e:
            print 'something wrong in prefixes list:',e
    if len(prefixes_list) > 1:
        df = pd.DataFrame(prefixes_list)
        df.loc[:, 'country'] = df['name'].str[0:2]
        return df 
    else:
        logger.warning('something wrong in lnetd_prefixes')

def lnetd_routers(new_list):
    routers_list = []
    for i in new_list:
        try:
            source = i.data[137][0]['V'][0]
            #print INDENT,'name',i.name
            #print INDENT,'132:',i.data[132]
            ip = i.data[132][0]['V'][0]
            routers = {"name": source,
                                "ip": ip}
            routers_list.append(routers)
            #print '-------'
        except Exception as e:
            print 'something wrong in router list',e
    if len(routers_list) > 1:
        df = pd.DataFrame(routers_list)
        df.loc[:, 'country'] = df['name'].str[0:2]
        df['vendor'] = df.apply(lambda row: get_sysdesc(row['name']),axis=1)
        df['version'] = 'NA' #for now
        return df 
    else:
        logger.warning('something wrong in lnetd_routers')
def lnetd_links(df):
    topology = []
    for i in new_list:
        try:
            source = i.data[137][0]['V'][0]
            #print INDENT,'name',i.name
            #print INDENT,'137:',i.data[137][0]['V'][0]
            for data_22 in i.data[22]:
                for n in data_22['V']:
                    #print 'this is the n:',n
                    #print 'this is the nodes_names',node_names
                    target = get_hostname(n['lsp_id'])
                    metric = n['metric']
                    l_ip = n['l_ip']
                    r_ip = n['r_ip']
                    #print ('%s,%s,%s') %(source,target,metric)
                    final_entry = {"source": source,
                                   "target": target,
                                   "metric": metric,
                                   "l_ip": l_ip,
                                   "r_ip": r_ip
                               }
                    #print '-----final_entry :',final_entry
                    topology.append(final_entry)
            #print '-------'
        except:
            logger.warning('something wrong in creating topology')
    #print 'final topology :\n',topology
    if len(topology) > 1:
        try:
            df = pd.DataFrame(topology)
            our_lsp_id = config.get('isisd', 'our_lsp') #'000.503.300.110'
            logger.info('Remove our lsp_id')
            df = remove_unreachable_nodes(df,source,our_lsp_id)
            logger.info('Generate l_ip r_ip pair')
            df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
            logger.info('Set l_ip r_ip pair as string')
            df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
            logger.info('Fill NA values with 0')
            df = df.fillna(0)
            #df['l_int'] = 34
            df['r_int'] = -1
            #df['util'] = random.randint(0,2000)
            #df['capacity'] = 1000
            #df['errors'] = random.randint(0,2000)
            df['l_int'] = df.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
            df['util'] = df.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
            df['capacity'] = df.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
            df['errors'] = df.apply(lambda row: get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)
            #print '\npanda after the function:\n{}'.format(df)
            #remove rows if both source and target are the same
            df = df.query("source != target")
        except Exception as e:
            print 'something went wrong on lnetd_links',e
            df = [] 
    return df 
def lnetd_data_sql_write(df,db):
    try:
        logger.info('Write to database')
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df.to_sql(db, disk_engine, if_exists='replace')
        logger.info('All done')
        logger.debug('here is the resulting info :\n %s' %(df))
    except Exception as e:
        logging.exception('Got error writing to sqlite3 db: %s') %e 
def remove_unreachable_nodes(df,source,our_lsp_id):
  """ find if from source to destinatio there is a path
  create a subgraph with all the nodes that we have path's to
  return this as panda frame
  """
  g = nx.from_pandas_edgelist(df, 'source', 'target', ['metric','l_ip','r_ip'],create_using =nx.MultiDiGraph())
  lst = list(nx.single_source_shortest_path_length(g, source))
  g.remove_node(our_lsp_id)
  g = g.subgraph(lst)
  df = nx.to_pandas_edgelist(g)
  return df

def get_hostname(sysid):
    """ Get the mapping 
    between sysid and hostname
    """
    try:
        name = node_names[sysid]
        return name
    except:
        return sysid

class ThreadingISISd(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            print('Running ISISd in background')
            run_it()
            time.sleep(self.interval)


lnetd_isis = ThreadingISISd()

while 1:
    time.sleep(20)
    INDENT  = "    "
    new_list = []
    #print 'new_list at begining',new_list
    new_nodes = copy.deepcopy(nodes)
    new_nodes.sort()
    #print new_nodes
    #pprint(new_nodes[0].data)
    #pprint(new_nodes[1].data)
    #print INDENT,'new_nodes:{}'.format(new_nodes)
    while len(new_nodes) != 0:
        cur_node = new_nodes[0]
        #cur_node.data = {}
        #print INDENT*2,'before extend data this is the data in cur_node\n'
        #pprint(cur_node.data)
        for n in range(1, len(new_nodes)):
            if cur_node.name == new_nodes[n].name:
                #print INDENT*3,'before extend data this is the data in new_nodes\n'
                #pprint(new_nodes[n].data)
                #print INDENT*3,'cur_node and next_node equal:',new_nodes[n].name
                for key, value in new_nodes[n].data.iteritems():
                    cur_node.data.setdefault(key, []).extend(value)
        new_nodes = [value for value in new_nodes if value.name != cur_node.name]
        #print 'whats remaining in new_nodes {}'.format(new_nodes)
        #print INDENT*2,'\nafter this is the data in cur_node\n'
        #pprint(cur_node.data)
        new_list.append(cur_node)

    node_names = {}
    #print 'this is the list now: {}'.format(topology)
    for i in new_list:
        try:
            node_names.update({i.name:i.data[137][0]['V'][0]})
        except:
            print 'error'
    #get routers
    try:
        links = lnetd_links(new_list)
        routers = lnetd_routers(new_list)
        prefixes = lnetd_prefixes(new_list)
        lnetd_data_sql_write(links,'Links')
        lnetd_data_sql_write(routers,'Routers')
        lnetd_data_sql_write(prefixes,'Prefixes')
    except Exception as e:
        print 'something wrong in writing to sql module: {}'.format(e)

