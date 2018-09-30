from flask import Blueprint, render_template, session
from flask_login import login_required
from collections import Counter,OrderedDict
import pandas as pd
import json
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from get_graph_fct_ifindex import get_graph_ifindex
from get_interface_ifName_fct import get_interface_ifName
from calculateSpf_fct import calculateSpf
from calculateSpf_latency_fct import calculateSpf_latency
from model_demand import model_demand_get
from database import db

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
    results = model_demand_get(df_links,demand_request)
    results_final = results.to_dict(orient='records')
    print "results: %s" %jsonify(results_final)
    return jsonify(results_final)


@blueprint.route('/spf_and_latency',methods=['GET', 'POST'])
def spf_and_latency():
    source = request.args['source']
    target = request.args['target']
    arr = request.args['arr']
    results = calculateSpf_latency(arr,source,target)
    print "results: %s" %jsonify(results)
    return jsonify(results)

@blueprint.route('/save_node_position',methods=['POST'])
@login_required
def save_node_position():
    current_user = session['user_id']
    arr = request.args['arr']
    df_node_position = pd.DataFrame(eval(arr))
    df_node_position=df_node_position.drop_duplicates()
    df_node_position['user'] = current_user
    #print "after duplicates {}".format(df_node_position)
    df_node_position.to_sql(name='Node_position_temp', con=db.engine, index=False, if_exists='replace')
    #hack due to panda limitation ; no if_exists='update'
    replace_sql = db.engine.connect()
    trans = replace_sql.begin()
    replace_sql.execute('INSERT OR REPLACE INTO Node_position (id,x,y,user) SELECT id,x,y,user FROM Node_position_temp;')
    trans.commit()
    #end hack , need a better way here , this is lame
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
