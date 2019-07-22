import networkx as nx
import pandas as pd
import sys
import random,string
import re

def add_demand(g,paths,demand_path):
    for p in paths:
        u=p[0]
        for v in p[1:]:
            min_weight = min(d['metric'] for d in g[u][v].values())
            keys = [k for k, d in g[u][v].items() if d['metric'] == min_weight]
            num_ecmp_links = len(keys)
            for k in keys:
                g[u][v][k]['util'] += int(demand_path)/ int(num_ecmp_links)
            u=v
    df_reverse = nx.to_pandas_edgelist(g)
    return(g)

def deploy_demand(lsps,arr,source,target,demand):
    #create df from array 
    df = pd.DataFrame(eval(arr))
    print('----df:\n',df)
    if len(lsps) > 0:
        df_lsps = pd.DataFrame(lsps)

        #df_lsps=df_lsps.drop(['Action','ero'], axis=1)
        #df_lsps['metric'] = 1
        df_lsps['l_ip_r_ip'] = ''.join(random.choices(df_lsps['index']  + string.digits, k=2))
        df_lsps['l_ip'] = ''.join(random.choices('lsp-' + df_lsps['index']  + string.digits, k=2))
        df_lsps['r_ip'] = ''.join(random.choices('lsp-' + df_lsps['index']  + string.digits, k=2))
        df_lsps['l_int'] = 0
        df_lsps['errors'] = 0
        df_lsps['capacity'] = 0
        df_lsps['metric'] = pd.to_numeric(df_lsps['metric'], errors='coerce')
        df_lsps['id'] = pd.to_numeric(df_lsps['id'], errors='coerce')
        df_lsps['index'] = pd.to_numeric(df_lsps['index'], errors='coerce')
        df_lsps['util'] = pd.to_numeric(df_lsps['util'], errors='coerce')

        df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
        df['index'] = pd.to_numeric(df['index'], errors='coerce')
        df['util'] = pd.to_numeric(df['util'], errors='coerce')
        df['ero'] = 'a,b'

        df_combined = pd.concat([df, df_lsps], axis=0).fillna(0)
    else:
        df['metric'] = pd.to_numeric(df['metric'], errors='coerce')
        df['index'] = pd.to_numeric(df['index'], errors='coerce')
        df['util'] = pd.to_numeric(df['util'], errors='coerce')
        df['ero'] = 'a,b'

        df_combined = pd.concat([df], axis=0).fillna(0)
    print('-----df_combined\n',df_combined)
    failsafe = False
    try:
        #create a nx graph from spf only
        g = nx.from_pandas_edgelist(df, 'source', 'target', ['l_int','capacity','ero','index', 'metric','l_ip','r_ip','util'],create_using =nx.MultiDiGraph())
        g_combined = nx.from_pandas_edgelist(df_combined, 'source', 'target', ['l_int','capacity','ero','index', 'metric','l_ip','r_ip','util'],create_using =nx.MultiDiGraph())
        #get all paths on the spf 
        paths = list(nx.all_shortest_paths(g, source, target, weight='metric'))
        #print ( 'this is the initial path:\n',paths)
        num_ecmp_paths = len(paths)
        demand_path = demand / int(len(paths))
        for p in paths:
            u=p[0]
            for v in p[1:]:
                #print(f'this is u:{u} and v:{v}')
                #iterate over lsp to see if the headend and tailend are in the path( no load balance at this stage)
                if failsafe == 100:
                    break
                #print(f'failsafe1:{failsafe1}  , len_lsp: {len(lsps)}')
                for lsp in lsps:
                    #print('did i get in for lsp in lsps')
                    if u == lsp['source'] and lsp['target'] in p:
                        #print('found headend + tailend in the path')
                        paths_with_lsp = list(nx.all_shortest_paths(g_combined, u, target, weight='metric'))
                        num_ecmp_paths_with_lsp = len(paths_with_lsp)
                        demand_path_with_lsp = demand_path / num_ecmp_paths_with_lsp
                        g_combined = add_demand(g_combined,paths_with_lsp,demand_path_with_lsp)
                        failsafe = 100
                        #print('did i break here ?\n')
                        break
                if failsafe == 100:
                    break
                #work the tree
                else:
                    min_weight = min(d['metric'] for d in g[u][v].values())
                    values_g=(g[u][v].values())
                    items_g=g[u][v].items()
                    keys = [k for k, d in g[u][v].items() if d['metric'] == min_weight]
                    num_ecmp_links = len(keys)
                    for k in keys:
                        g[u][v][k]['util'] += int(demand_path)/int(num_ecmp_links)

                u=v
        if g_combined.number_of_edges() > 1:
            #generate new panda from networkx 
            df_g = nx.to_pandas_edgelist(g)
            #print(f'this is the df_g{df_g}')
            df_g_combined = nx.to_pandas_edgelist(g_combined)
            #print(f'this is the df_g_combined{df_g_combined}')
            #combined and sum util 
            df_reverse = pd.concat([df_g, df_g_combined]).groupby(['l_int','capacity','ero','source','target','r_ip','l_ip','metric','index'], as_index=False)["util"].sum()
            #remove lsp from panda into another panda
            regex_pat = re.compile(r'^lsp.+', flags=re.IGNORECASE)
            df_lsps = df_reverse[df_reverse['l_ip'].str.match(regex_pat)]
            df_lsps['id'] = df_lsps['index']
            df_reverse = df_reverse[~df_reverse['l_ip'].str.match(regex_pat)]
            lsps_final = df_lsps.to_dict(orient='records')
        else:
            df_reverse = nx.to_pandas_edgelist(g)
        return df_reverse,lsps_final
    except Exception as error:
        print(error)
        df_demand = pd.DataFrame()
        return df_demand

def lsp_demands(lsps,arr,source,target,demand):
    df = deploy_demand(lsps,arr,source,target,demand)
    df_final = df[0]
    print('lsps_dict:',df[1])
    for lsp_id in df[1]:
        for nn in lsp_id['ero'].split(','):
            df_final.loc[(df_final['r_ip'] == nn),'util'] = df_final['util'] + int(lsp_id['util'])
    df_final = df_final.drop(['ero','index'], axis=1)
    #add attributes back
    df_final['errors'] = '0'
    df_final['Action'] = ''
    #print(df_final.l_ip.values.tolist())
    #print(df_final.r_ip.values.tolist())
    df_final = df_final.reset_index()
    df_final.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df_final.l_ip.values.tolist(), df_final.r_ip.values.tolist()))])
    df_final['id'] = df_final['index']
    #print('this is the final \n',df_final)
    lsps_final = df[1]
    return df_final,lsps_final
