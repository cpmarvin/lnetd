from isis_v02  import *
import threading
import time
import pandas as pd
import networkx as nx

def remove_unreachable_nodes(df,source):
  """ get find if from source to destinatio there is a path
  create a subgraph with all the nodes that we have path's to
  return this as panda frame
  """
  g = nx.from_pandas_edgelist(df, 'source', 'target', ['metric','l_ip','r_ip'],create_using =nx.MultiDiGraph())
  lst = list(nx.single_source_shortest_path_length(g, source))
  g = g.subgraph(lst)
  return nx.to_pandas_edgelist(g)

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
    new_nodes = nodes
    new_nodes.sort()
    #print INDENT,'new_nodes:{}'.format(new_nodes)
    while len(new_nodes) != 0:
        cur_node = new_nodes[0]
        #cur_node.data = {}
        for n in range(1, len(new_nodes)):
            if cur_node.name == new_nodes[n].name:
                #print INDENT*3,'cur_node and next_node equal:',new_nodes[n].name
                for key, value in new_nodes[n].data.iteritems():
                    cur_node.data.setdefault(key, []).extend(value)
        new_nodes = [value for value in new_nodes if value.name != cur_node.name]
        #print 'whats remaining in new_nodes {}'.format(new_nodes)
        #print INDENT*5,cur_node.data
        new_list.append(cur_node)

    node_names = {}
    topology = []
    #print 'this is the list now: {}'.format(topology)
    for i in new_list:
        try:
            node_names.update({i.name:i.data[137][0]['V'][0]})
        except:
            print 'error'
    #print 'nodes_names : \n',node_names
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
            print 'something wrong'
    #print 'final topology :\n',topology
    df = pd.DataFrame(topology)
    df.drop_duplicates()
    our_lsp_id = '000.503.300.110'
    source = df.loc[df['target'] == our_lsp_id ].head(1).to_dict(orient='records')[0]['source']
    #print 'source:{}'.format(source)
    #print '\nthis is before:\n {}'.format(df)
    df = remove_unreachable_nodes(df,source)
    print '\nthis is after:\n {}'.format(df)
    #pprint (nodes)
