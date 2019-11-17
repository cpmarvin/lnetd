import networkx as nx
import pandas as pd


def calculateSpf_latency(arr,source,target):
    df = pd.DataFrame(eval(arr))
    d3js_links =[]
    return_total_metric = []
    df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
    df['id'] = pd.to_numeric(df['id'], errors='coerce')
    g = nx.from_pandas_edgelist(df, 'source', 'target', ['id', 'metric','latency'],create_using =nx.MultiDiGraph())
    paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
    num_ecmp_paths = len(paths)
    for p in paths:
            u=p[0]
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
                    values_g=(g[u][v].values())
                    items_g=g[u][v].items()
                    for d in values_g:
                        if d['metric'] == min_weight:
                            d3js_links.append(d)
                            if min_latency_link == 0:
                                total_metric = total_metric + int(min_latency1)
                                min_latency_link = 1
                    u=v
            return_total_metric.append(total_metric)
    return d3js_links,max(return_total_metric)

