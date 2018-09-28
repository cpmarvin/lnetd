import networkx as nx
import pandas as pd


def calculateSpf(arr,source,target):
	df = pd.DataFrame(eval(arr))
	d3js_links =[]
	df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
	df['id'] = pd.to_numeric(df['id'], errors='coerce')

	g = nx.from_pandas_edgelist(df, 'source', 'target', ['id', 'metric','l_ip','r_ip'],create_using =nx.MultiDiGraph())
	paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
	num_ecmp_paths = len(paths)
	for p in paths:
		u=p[0]
		for v in p[1:]:
			min_weight = min(d['metric'] for d in g[u][v].values())
			values_g=(g[u][v].values())
			items_g=g[u][v].items()
			for d in values_g:
				if d['metric'] == min_weight:
					d3js_links.append(d)
			u=v
	print d3js_links
        return d3js_links








