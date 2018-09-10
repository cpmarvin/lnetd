import networkx as nx
import pandas as pd


def calculateSpf_latency(arr,source,target):
        df = pd.DataFrame(eval(arr))
        d3js_links =[]
        return_total_metric = []
        #df = pd.DataFrame(arr)
        df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
        df['id'] = pd.to_numeric(df['id'], errors='coerce')

        g = nx.from_pandas_edgelist(df, 'source', 'target', ['id', 'metric','latency'],create_using =nx.MultiDiGraph())

        paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
        num_ecmp_paths = len(paths)
        print "number of paths: %s" %num_ecmp_paths
        print "this are the paths: %s" %paths

        for p in paths:
                u=p[0]
                print "new path_found : %s" %p
                total_metric = 0
                min_latency = []
                for v in p[1:]:
                        min_latency_link = 0
                        min_weight = min(d['metric'] for d in g[u][v].values())
                        for d in g[u][v].values():
                            if d['metric'] == min_weight:
                                min_latency.append(int(d['latency']))
                        min_latency1 = max(min_latency)
                        min_latency = []
                        #min_latency = max(float(d['latency']) for d in g[u][v].values())
                        print "path min metric:%s" %min_weight
                        print "max latency: %s" %min_latency
                        #total_metric = total_metric + min_weight
                        #print "u variable:%s" %u
                        #print "v variable:%s" %v
                        values_g=(g[u][v].values())
                        #print values_g
                        items_g=g[u][v].items()
                        #print items_g
                        #print "g[u][v].values() :%s" %values_g
                        #print "g[u][v].items() :%s" %items_g
                        for d in values_g:
                            if d['metric'] == min_weight:
                                d3js_links.append(d)
                                #total_metric = total_metric + int(min_latency1)
                                if min_latency_link == 0:
                                    total_metric = total_metric + int(min_latency1)
                                    min_latency_link = 1
                                #if float(d['latency']) <= min_latency:
                                #    if min_latency_link == 0:
                                #        total_metric = total_metric + min_latency 
                                #        #float(d['latency'])
                                #        min_latency_link = 1
                        u=v
                print " total path metric : %s " %total_metric
                return_total_metric.append(total_metric)
        print "max path metric %s" %max(return_total_metric)        
        print d3js_links
        return d3js_links,max(return_total_metric)

