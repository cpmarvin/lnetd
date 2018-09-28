import networkx as nx
import pandas as pd


def deploy_demand(arr,source,target,demand):
    df = arr
    d3js_links =[]
    df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
    df['index'] = pd.to_numeric(df['index'], errors='coerce')
    df['util'] = pd.to_numeric(df['util'], errors='coerce')
    try:
        g = nx.from_pandas_edgelist(df, 'source', 'target', ['index', 'metric','l_ip','r_ip','util'],create_using =nx.MultiDiGraph())
        paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
        num_ecmp_paths = len(paths)
        demand_path = demand / int(len(paths))
        for p in paths:
            u=p[0]
            for v in p[1:]:
                min_weight = min(d['metric'] for d in g[u][v].values())
                values_g=(g[u][v].values())
                items_g=g[u][v].items()
                keys = [k for k, d in g[u][v].items() if d['metric'] == min_weight]
                print "keys: %s" %keys
                num_ecmp_links = len(keys)
                for k in keys:
                    g[u][v][k]['util'] += int(demand_path)/int(num_ecmp_links)
                    print "test: %s" %g[u][v][k]
                u=v
        df_reverse = nx.to_pandas_edgelist(g)
        return df_reverse
    except Exception as error:
        print "Error in deploy_demand.py:%s " %error
        df_demand = pd.DataFrame()
        return df_demand
