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
from objects.models import Routers,Links,Links_latency,Node_position
from objects.models import External_topology_temp,External_position
from objects.models import Links_time

from api.mutils import *

blueprint = Blueprint(
    'api_blueprint', 
    __name__, 
    url_prefix = '/api', 
    template_folder = 'templates',
    static_folder = 'static'
    )

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

@blueprint.route('/model_demand')
@login_required
def model_demand():
    demand_request = request.args['demand']
    arr = request.args['arr']
    df_links = pd.DataFrame(eval(arr))
    #df_links = df_links.replace({'\t': ''}, regex=True)
    results = model_demand_get(df_links,demand_request)
    results_final = results.to_dict(orient='records')
    return jsonify(results_final)


@blueprint.route('/spf_and_latency',methods=['GET', 'POST'])
def spf_and_latency():
    source = request.args['source']
    target = request.args['target']
    arr = request.args['arr']
    results = calculateSpf_latency(arr,source,target)
    return jsonify(results)

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
