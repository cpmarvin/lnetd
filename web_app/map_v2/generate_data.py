from .mutils import *

def generate_data(name,router_ip,ifindex):
    try:
        df = get_demand_newtflow(router_ip,ifindex)
        df.columns= ['source','target','util','asn']
        df['source'] = df.apply(lambda row: get_hosname(row['source']),axis=1)
        df['target'] = df.apply(lambda row: get_hosname(row['target']),axis=1)
        df['cc'] = df.apply(lambda row: return_cc(row['target']),axis=1)
        df['asn'] = df.apply(lambda row: 'ASN-%s' %row['asn'],axis=1)
        df['asn'] = df['asn'].astype(str)
        df['source'] = df['source'].astype(str)
        df['target'] = df['target'].astype(str)
        df['cc'] = df['cc'].astype(str)
        df['util'] = df.apply(lambda row: row['util'] * 8 / 300,axis=1)
        df['source'] = name
        df_asn_to_cc = df.groupby(['source','cc']).sum().reset_index()
        df_asn_to_cc.columns=['source','target','util']
        df_rtr_to_casn = df.groupby(['target','asn']).sum().reset_index()
        df_rtr_to_casn.columns=['source','target','util']
        df.pop('source')
        df.pop('asn')
        new_order = [2,0,1]
        df = df[df.columns[new_order]]
        df.columns=['source','target','util']
        df_final = pd.concat([df, df_asn_to_cc,df_rtr_to_casn]).groupby(['source','target'],as_index=False).sum()
        df_final.reset_index(drop=True)
        return df_final.to_dict(orient='records')
    except Exception as e:
        print(e)
