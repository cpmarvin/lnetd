from flask import Blueprint, render_template, session
from flask_login import login_required
from collections import Counter,OrderedDict
import pandas as pd
import json
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin

from .get_graph_fct_ifindex import get_graph_ifindex
from .get_interface_ifName_fct import get_interface_ifName
from .get_graph_fct_ifname import get_graph_ifname
from .get_graph_fct_aggregated import get_graph_aggregated
from .calculateSpf_fct import calculateSpf
from .calculateSpf_latency_fct import calculateSpf_latency
from .model_demand import model_demand_get

from database import db
from objects_v2.models import Routers,Links,Links_latency,Node_position
from objects_v2.models import External_topology_temp,External_position
from objects_v2.models import Links_time,Links_Model,External_topology_time

from api_v2.mutils import *

#test new lsp demands
from .lsp_deploy_demands import lsp_demands

from base_v2.models import User
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    return True

blueprint = Blueprint(
    'api_blueprint', 
    __name__, 
    url_prefix = '/api', 
    template_folder = 'templates',
    static_folder = 'static'
    )

@blueprint.route('/get_topology',methods=['GET'])
@auth.login_required
def get_topology():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    df.drop(['util','index','l_int', 'l_ip_r_ip', 'errors'], axis=1, inplace=True)
    df.rename({'l_ip': 'local_ip', 'r_ip': 'remote_ip'}, axis=1,inplace=True)
    df_node = pd.read_sql(db.session.query(Node_position).filter(Node_position.id >=0).statement,db.session.bind)
    df_node.rename({'id':'name'}, axis=1,inplace=True)
    df_node['x'] = df_node['x'].astype(float)
    df_node['y'] = df_node['y'].astype(float)
    topology_dict = {}
    topology_dict['links'] = df.to_dict(orient='records')
    topology_dict['nodes'] = df_node.to_dict(orient='records')
    return jsonify(topology_dict)

@blueprint.route('/ifName',methods=['GET', 'POST'])
@login_required
def ifName():
    ip = request.args['ip']
    host = request.args['host']
    results = get_interface_ifName(host,ip)
    return results

@blueprint.route('/graph_ifindex')
@login_required
def graph():
    ip = request.args['ip']
    host = request.args['host']
    results = get_graph_ifindex(host,ip)
    return results

@blueprint.route('/graph_ifname')
@login_required
def graph_ifname():
    interface = request.args['interface']
    host = request.args['host']
    direction = request.args['direction']
    results = get_graph_ifname(host,interface,direction)
    return results

@blueprint.route('/graph_aggregated')
@login_required
def graph_aggregated():
    source = request.args['source']
    target = request.args['target']
    results = get_graph_aggregated(source,target)
    return results

@blueprint.route('/spf')
@login_required
def spf():
    source = request.args['source']
    target = request.args['target']
    arr = request.args['arr']
    results = calculateSpf(arr,source,target)
    return jsonify(results)

@blueprint.route('/model_lsp_demand')
@login_required
def model_lsp_demand():
    demand_request = request.args['demand']
    arr = request.args['arr']
    df_links = pd.DataFrame(eval(arr))
    lsps = eval(request.args['lsps'])
    print(f'this is the lsps:{lsps}')
    # create an empty frame
    df_all_demands = pd.DataFrame()
    df_all_lsps = []
    for entry in eval(demand_request):
        source = entry['source']
        target = entry['target']
        demand = entry['demand']
        results_array = lsp_demands(lsps,arr,source,target,demand)
        df_all_demands = pd.concat([df_all_demands, results_array[0]], axis=0)
        df_all_lsps.extend(results_array[1])
    df_final = df_all_demands.groupby(['index','l_int','capacity','source','target','r_ip','l_ip','metric','errors','Action','l_ip_r_ip'] , as_index=False)['util'].sum()
    df_final['l_ip_r_ip'] = df_final['l_ip_r_ip'].astype(str)
    df_final_lsps = pd.DataFrame(df_all_lsps)
    if len(lsps) > 0:
        print('lsp before merge\n',df_final_lsps)
        df_final_lsps = df_final_lsps.groupby(['id','capacity','ero','index','l_ip','metric','r_ip','source','target'] , as_index=False)['util'].sum()
        print('lsp after merge\n',df_final_lsps)
    else:
        df_final_lsps = pd.DataFrame()

    results_final = df_final.to_dict(orient='records')
    df_final_lsps = df_final_lsps.to_dict(orient='records')
    return jsonify(results_final,df_final_lsps)

@blueprint.route('/model_demand')
@login_required
def model_demand():
    demand_request = request.args['demand']
    arr = request.args['arr']
    print('this is the array',arr)
    df_links = pd.DataFrame(eval(arr))
    #df_links = df_links.replace({'\t': ''}, regex=True)
    from datetime import datetime
    print('start_time',datetime.now())
    results = model_demand_get(df_links,demand_request)
    print('end_time',datetime.now())
    results_final = results.to_dict(orient='records')
    return jsonify(results_final)


@blueprint.route('/spf_and_latency',methods=['GET', 'POST'])
def spf_and_latency():
    source = request.args['source']
    target = request.args['target']
    arr = request.args['arr']
    results = calculateSpf_latency(arr,source,target)
    return jsonify(results)

@blueprint.route('/save_node_position_global', methods=['POST'])
@login_required
def save_node_position_global():
  try:
    current_user = session['user_id']
    map_type = request.args['map_type']
    arr = request.args['arr']
    df_node_position = pd.DataFrame(eval(arr))
    df_node_position = df_node_position.drop_duplicates()
    df_node_position['user'] = current_user
    df_node_position['map_type'] = map_type
    sql_inserts = SQL_INSERT_UPDATE_FROM_DATAFRAME(
        df_node_position, 'node_position_global')
    replace_sql = db.engine.connect()
    trans = replace_sql.begin()
    for sql_entry in sql_inserts:
      replace_sql.execute(sql_entry)
    trans.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
  except Exception as e:
    raise

@blueprint.route('/save_node_position',methods=['POST'])
@login_required
def save_node_position():
    current_user = session['user_id']
    arr = request.args['arr']
    df_node_position = pd.DataFrame(eval(arr))
    df_node_position=df_node_position.drop_duplicates()
    df_node_position['user'] = current_user
    df_node_position.to_sql(name='Node_position_temp', con=db.engine, index=False, if_exists='replace')
    #hack due to panda limitation ; no if_exists='update'
    replace_sql = db.engine.connect()
    trans = replace_sql.begin()
    replace_sql.execute('INSERT OR REPLACE INTO Node_position (id,x,y,user) SELECT id,x,y,user FROM Node_position_temp;')
    trans.commit()
    #end hack , need a better way here , this is lame
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@blueprint.route('/get_isis_links',methods=['GET'])
@login_required
def get_isis_links():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return jsonify(isis_links)   

@blueprint.route('/get_isis_nested_links',methods=['GET'])
@login_required
def get_isis_nested_links():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    df['node'] = df['source']
    df['source'] = df.apply(lambda row: row['source'][:2],axis=1)
    df['target'] = df.apply(lambda row: row['target'][:2],axis=1)
    df = df[df['source'] != df['target']]
    isis_links = df.to_dict(orient='records')
    return jsonify(isis_links)

@blueprint.route('/save_external_position',methods=['POST'])
@login_required
def save_external_position():
    current_user = session['user_id']
    arr = request.args['arr']
    df_node_position = pd.DataFrame(eval(arr))
    df_node_position=df_node_position.drop_duplicates()
    df_node_position['user'] = current_user
    df_node_position.to_sql(name='External_position', con=db.engine, index=False, if_exists='replace')
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@blueprint.route('/save_topology',methods=['POST'])
@login_required
def save_topology():
    print('did i run this')
    arr = request.args['arr']
    print(arr)
    df = pd.DataFrame(eval(arr))
    df = df.drop(['','index','Action','id'], axis=1)
    print(df.dtypes,df.columns)
    #df = df.reset_index()
    print(df.dtypes,df.columns) 
    #df.columns = ['index','direction','icon','interface','node','source','target']
    print(df.to_dict(orient='records'))
    df.to_sql(name='External_topology_temp', con=db.engine, if_exists='replace' )
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@blueprint.route('/get_isis_links_time',methods=['GET'])
@login_required
def get_isis_links_time():
    start_time = request.args['time']
    df = pd.read_sql(db.session.query(Links_time).filter(Links_time.timestamp == start_time).statement,db.session.bind)
    #print(df)
    isis_links = df.to_dict(orient='records')
    return jsonify(isis_links)

@blueprint.route('/get_external_links_time',methods=['GET'])
@login_required
def get_external_links_time():
    start_time = request.args['time']
    df = pd.read_sql(db.session.query(External_topology_time).filter(External_topology_time.timestamp == start_time).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return jsonify(isis_links)

@blueprint.route('/get_isis_links_model',methods=['GET'])
@login_required
def get_isis_links_model():
    model_name = request.args['model_name']
    df = pd.read_sql(db.session.query(Links_Model).filter(Links_Model.model_name == model_name).statement,db.session.bind)
    df['id'] = df.index
    print(df)
    isis_links = df.to_dict(orient='records')
    return jsonify(isis_links)

@blueprint.route('/get_links_interval',methods=['GET'])
@login_required
def get_links_interval():
    start_time = request.args['time']
    df = pd.read_sql(db.session.query(Links_time.timestamp).filter(Links_time.timestamp >= start_time).distinct(Links_time.timestamp).limit(20).statement,db.session.bind)
    values = df['timestamp'].astype(str).unique().tolist()
    return jsonify(values)

@blueprint.route('/get_external_interval',methods=['GET'])
@login_required
def get_external_interval():
    start_time = request.args['time']
    df = pd.read_sql(db.session.query(External_topology_time.timestamp).filter(External_topology_time.timestamp >= start_time).distinct(External_topology_time.timestamp).limit(20).statement,db.session.bind)
    values = df['timestamp'].astype(str).unique().tolist()
    return jsonify(values)


@blueprint.route('/save_layer1_topology',methods=['POST'])
@login_required
def save_layer1_topology():
    arr = request.args['arr']
    df = pd.DataFrame(eval(arr))
    df.set_index("id", inplace = True)
    #df = df.drop(['','index','Action','id'], axis=1)
    df.to_sql(name='Layer1Topology', con=db.engine, if_exists='replace' )
    print(df)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@blueprint.route('/save_international_pop',methods=['POST'])
@login_required
def save_international_pop():
    arr = request.args['arr']
    df = pd.DataFrame(eval(arr))
    df = df.drop(['','index','Action','id'], axis=1)
    df.to_sql(name='International_PoP_temp', con=db.engine, if_exists='replace' )
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@blueprint.route('/get_forecast',methods=['GET'])
@login_required
def get_forecast():
    '''
    Get forcast by source and destination
    for next 30 days
    '''
    source = request.args['source']
    target = request.args['target']
    df = generate_forecast(source, target)
    return jsonify(df)

@blueprint.route('/save_bgp_peering',methods=['POST'])
@login_required
def save_bgp_peering():
    arr = request.args['arr']
    df = pd.DataFrame(eval(arr))
    df = df.drop(['','index','Action','id'], axis=1)
    df.to_sql(name='Bgp_peering_points', con=db.engine, if_exists='replace' )
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

#save model 
@blueprint.route('/save_links_model',methods=['POST'])
@login_required
def save_links_model():
    print('this is the request',request)
    current_user = str(session['user_id'])
    model_name = str(request.args['model_name'])
    arr = request.args['arr']
    df = pd.DataFrame(eval(arr))
    df['user_id'] = current_user
    df['model_name'] = model_name
    # delete old entries matching model_name and username
    replace_sql = db.engine.connect()
    trans = replace_sql.begin()
    sql_query = 'DELETE from Links_Model where user_id = "%s" and model_name = "%s" ' %(current_user,model_name)
    replace_sql.execute(sql_query)
    trans.commit()
    # update with new values 
    #df.to_sql(name='Links_Model', con=db.engine, if_exists='fail' )
    def SQL_INSERT_STATEMENT_FROM_DATAFRAME(SOURCE, TARGET):
        sql_texts = []
        for index, row in SOURCE.iterrows():       
            sql_texts.append('INSERT INTO '+TARGET+' ('+ str(', '.join(SOURCE.columns))+ ') VALUES '+ str(tuple(row.values)))        
        print('\n\n'.join(sql_texts))
        print(sql_texts)
        return sql_texts
    sql_inserts = SQL_INSERT_STATEMENT_FROM_DATAFRAME(df,'Links_Model')
    trans = replace_sql.begin()
    for i in sql_inserts:
        replace_sql.execute(i)
    trans.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
