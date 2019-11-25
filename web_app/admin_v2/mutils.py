import networkx as nx
import pandas as pd
from  operator import itemgetter

def return_total_metric(paths,g):
    total_metric = []
    for p in paths:
        path_metric = 0
        u=p[0]
        for v in p[1:]:
            min_weight = min(d['metric'] for d in g[u][v].values())
            path_metric = path_metric + min_weight
            u=v
        total_metric.append(path_metric)
    return min(total_metric)

def network_report(df):
    network_report = {}
    df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
    g1 = nx.from_pandas_edgelist(df, 'source', 'target', ['index', 'metric','l_ip','r_ip','status'],create_using =nx.MultiDiGraph())
    import copy
    g = copy.deepcopy(g1)
    #iterate over links in the first g1 graph and remove them from g graph , need a better way
    for u,v,key,data in g1.edges(data=True,keys=True):
        if data['status'] !='up':
            print(u,v,key)
            g.remove_edge(u,v,key=key)
    g_undirected = g.to_undirected()
    network_report['Connected Network']  = nx.is_connected(g_undirected)
    network_report['Number of Nodes'] = g_undirected.number_of_nodes()
    network_report['Number of Links'] = g_undirected.number_of_edges()
    network_report['Network Density'] = nx.density(g_undirected)
    if nx.is_connected(g_undirected):
        network_report['Network Diameter'] = nx.diameter(g_undirected)
    else:
        network_report['Network Diameter'] = 0
    degree_dict = dict(g_undirected.degree(g_undirected.nodes(),weight=''))
    sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)
    network_report['Connectivity Node Degree'] = sorted_degree
    network_nodes = sorted(list(g.nodes))
    network_report['paths'] = []
    for node in network_nodes:
        source = node
        target_nodes = [ node for node in network_nodes if node!=source]
        for target in target_nodes:
            try:
                paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
                num_ecmp_paths = len(paths)
                total_metric = return_total_metric(paths,g)
                entry = {'source':source,'target':target,'ecmp_paths':num_ecmp_paths,'path_metric':total_metric,'note':'ok'}
            except nx.NetworkXNoPath as e:
                #print(dir(e))
                entry = {'source':source,'target':target,'ecmp_paths':'None','path_metric':'None','note':'NoPath'}
                pass
            except Exception as ee:
                pass
            network_report['paths'].append(entry)
    return network_report

def generate_network_report(initial_network=None,failed_network=None,compare=False):
    network_reports = {'initial_network':{},'failed_network':{}}
    initial_network_report = network_report(initial_network)
    network_reports['initial_network'] = initial_network_report
    if compare:
        failed_network_report = network_report(failed_network)
        network_reports['failed_network'] = failed_network_report

    return network_reports
