import networkx as nx
import pandas as pd


def deploy_demand(arr,source,target,demand):
    df = arr
    df['util']=0
    #print df
    d3js_links =[]
    #print "panda in function : %s" %df
    df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
    df['index'] = pd.to_numeric(df['index'], errors='coerce')

    g = nx.from_pandas_edgelist(df, 'source', 'target', ['index', 'metric','l_ip','r_ip','util'],create_using =nx.MultiDiGraph())
    paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
    num_ecmp_paths = len(paths)
    demand = demand / int(len(paths))
    ecmp_links = 0
    #print "number of paths: %s" %num_ecmp_paths
    #print "this are the paths: %s" %paths
    #demand = 10
    print df
    for p in paths:
        #print "All nodes  in path: %s" %p
        u=p[0]
        for v in p[1:]:
            #print "path betwen p[0] si v in p[:1]: %s" %v
            min_weight = min(d['metric'] for d in g[u][v].values())
            #print "u variable:%s" %u
            #print "v variable:%s" %v
            values_g=(g[u][v].values())
            items_g=g[u][v].items()
            #print "g[u][v].values() :%s" %values_g
            #print "g[u][v].items() :%s" %items_g
            for d in values_g:
                if d['metric'] == min_weight:
                    #print "print d :%s" %d
                    ecmp_links = ecmp_links +1
                    #d3js_links.append(d)
            #print "number of ECMP links between nodes :%s" %ecmp_links
            #print "demand for each links is : %s" %(int(demand)/int(ecmp_links))
            for d in values_g:
                if d['metric'] == min_weight:
                    print d['util']
                    if ( d['util'] == demand ):
                        d['util'] = d['util']
                    else:
                        d['util'] = int(d['util']) + int(demand)/int(ecmp_links)
                    d3js_links.append(d)
            ecmp_links = 0
            u=v
    df_demand = pd.DataFrame(d3js_links)
    #print "initial panda \n %s " %df
    #print "resulting panda with demand \n %s" %df_demand
    #print "merge pandas on l_ip\n"
    #df_merge = pd.merge(df,df_demand)
    #print "resulting panda \n%s" %df_merge
    return df_demand

