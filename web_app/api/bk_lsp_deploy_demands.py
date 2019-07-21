import networkx as nx
import pandas as pd
import sys

def deploy_lsp_demand(lsps,arr,source,target,demand):
    #create df from array
    print(f'this is the array:{arr}')
    print(f'this is the lsps:{type(lsps)}')
    df = pd.DataFrame(eval(arr))
    #df=df.drop(['Action'], axis=1)
    d3js_links =[]
    df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
    df['index'] = pd.to_numeric(df['index'], errors='coerce')
    df['util'] = pd.to_numeric(df['util'], errors='coerce')
    failsafe = False
    lsp_id = 0
    lsps_indexes = []
    jump = 0
    try:
        #create a nx graph from spf only
        g = nx.from_pandas_edgelist(df, 'source', 'target', ['index', 'metric','l_ip','r_ip','util'],create_using =nx.MultiDiGraph())
        #get all paths on the spf 
        paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
        print ( 'this is the initial path:\n',paths)
        num_ecmp_paths = len(paths)
        demand_path = demand / int(len(paths))
        for p in paths:
            print('iterate on path :',p)
            # u is the first node in the path
            u=p[0]
            n=1
            v=p[n]
            while n < len(p):
                #v=p[n]
                '''
                print('this is n:',n)
                print('this is u:',u)
                print('this is v:',v)
                '''
                #iterate over lsp to see if the headend and tailend are in the path( no load balance at this stage)
                for lsp in lsps:
                    print(f'this is the lsp : {lsp}')
                    if u == lsp['source'] and lsp['target'] in p:
                        print('found headend + tailend in the path')
                        lsp_demand = demand_path
                        print(f'the lsp {lsp} will have a demand of {lsp_demand}')
                        #lsp['util'] = lsp_demand
                        lsps_indexes.append(lsp_id)
                        lsp_id += 1
                        print(f'updated lsp is {lsp}')
                        print('moving u to tailend')
                        #move u to lsp tailend
                if len(lsps_indexes) > 0 and jump == 0:
                    u = lsps[1]['target']
                    jump = 1
                    if u == target:
                        failsafe = 100
                    else:
                        v = p[p.index(u)+1]
                        #move v to the next node ( will break if lsp is not core to core , failsafe is for that )
                print('not found source and target in path')
                if failsafe == 100:
                    break
                if p.index(v) == len(p)-1:
                    print('v is the last one ')
                    min_weight = min(d['metric'] for d in g[u][v].values())
                    keys = [k for k, d in g[u][v].items() if d['metric'] == min_weight]
                    num_ecmp_links = len(keys)
                    for k in keys:
                        print(g[u][v][k]['util'])
                        g[u][v][k]['util'] += int(demand_path)/int(num_ecmp_links)
                        print(f'****for k in keys : did i get here : u:{u},v:{v}')
                    n = 100
                    break
                #work the tree
                else:
                    print(f'this is the else on work tree and my u:{u} and v:{v}')
                    min_weight = min(d['metric'] for d in g[u][v].values())
                    values_g=(g[u][v].values())
                    items_g=g[u][v].items()
                    keys = [k for k, d in g[u][v].items() if d['metric'] == min_weight]
                    num_ecmp_links = len(keys)
                    for k in keys:
                        g[u][v][k]['util'] += int(demand_path)/int(num_ecmp_links)
                        print(f'****for k in keys : did i get here : u:{u},v:{v}')
                        print(g[u][v])

                if v == p[len(p)-1]:
                    print('equal')
                    u = u
                    v = v 
                else:
                    u=v
                print(f'now is : u:{u},v:{v}')
                where_v = p.index(u)+1
                print(f'where_v:{where_v}')
                v = p[where_v]
                print(f'now is : u:{u},v:{v}')
                #n = n + 1
                print(f'after end of path condition : did i get here : u:{u},v:{v}')
                print(f'------------- here n get +1 => {n}')
        df_reverse = nx.to_pandas_edgelist(g)
        return df_reverse,lsps_indexes
    except Exception as error:
        print(error)
        df_demand = pd.DataFrame()
        return df_demand

def lsp_demands(lsps,arr,source,target,demand):
    df = deploy_lsp_demand(lsps,arr,source,target,demand)
    df_final = df[0]
    df_final['util'] = df_final['util'].astype(int)
    print('this is the df final in lsp_demands\n',df_final)
    if df[1]:
        print(df[1])
        for lsp_id in df[1]:
            print(f'lsp_id :{lsp_id}')
            print(f'lsp : {lsps[lsp_id]}')
            for nn in lsps[lsp_id]['ero'].split(','):
                print(f'the nn is :{nn}')
                df_final.loc[(df_final['r_ip'] == nn),'util'] = df_final['util'] + int(lsps[lsp_id]['util']) + int(demand/(len(df[1])))
                print(f'this is the df after traffic deloyed:\n {df_final}')
            lsps[lsp_id]['util'] = int(demand/(len(df[1]))) + int(lsps[lsp_id]['util'])
    print(df_final,lsps)
    df_final['util'] = df_final['util'].astype(int)
    return df_final,lsps
