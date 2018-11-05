from flask import Blueprint, render_template, request ,session 
from flask_login import login_required
from objects.models import Routers,Links,Links_latency,Node_position
from database import db
from collections import Counter,OrderedDict
import pandas as pd
from get_demand_netflow import *
import json 

blueprint = Blueprint(
    'data_blueprint', 
    __name__, 
    url_prefix = '/data', 
    template_folder = 'templates',
    static_folder = 'static'
    )

@blueprint.route('/isp_pops')
@login_required
def isp_pops():
    routers = Routers.query.all()
    country =  Counter(k.country for k in routers)    
    sample_data =dict(country)
    return render_template('isp_pops.html' , sample_data = sample_data)

@blueprint.route('/topology')
@login_required
def topology():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user ).statement,db.session.bind)
    #print 'node_position ------: {}'.format(node_position)
    node_position = node_position.to_dict(orient='records')
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return render_template('topology.html', values=isis_links, node_position=node_position)

@blueprint.route('/topology_errors')
@login_required
def topology_errors():
    current_user = str(session['user_id'])
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    #print isis_links
    return render_template('topology_errors.html', values=isis_links, node_position=node_position)

@blueprint.route('/topology_latency')
@login_required
def topology_latency():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    df = pd.read_sql(db.session.query(Links_latency).filter(Links_latency.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    #print isis_links
    return render_template('topology_latency.html', values=isis_links, node_position=node_position)

@blueprint.route('/filter_topology',methods=['GET', 'POST'])
@login_required
def filter_topology():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    source_filter = request.form.get('source_filter')
    target_filter = request.form.get('source_filter')
    #print source_filter
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return render_template('filter_topology.html',values=isis_links,source_filter = source_filter,target_filter=target_filter, node_position=node_position)


@blueprint.route('/model_demand', methods=['GET', 'POST'])
@login_required
def model_demand():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    #print 'node position ---------: {}'.format(node_position)
    netflow_demands = get_demand_netflow()
    #netflow_demands = [ {'source':'gb-p10-lon','target':'fr-p7-mrs','demand':1000000000} ]
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    df['util'] = 0
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    router_name = df_router_name['anon_1'].values.tolist()
    #print isis_links
    columns = [
            { "field": "state","checkbox":True},
            { "field": "id","title":"id","sortable":False},
            { "field": "index","title":"index","sortable":False},
            { "field": "source","title":"source","sortable":True,"editable":True},
            { "field": "target","title":"target","sortable":False,"editable":True},
            { "field": "l_ip","title":"l_ip","sortable":False,"editable":True},
            { "field": "metric","title":"metric","sortable":False,"editable":True},
            { "field": "l_int","title":"l_int","sortable":False},
            { "field": "r_ip","title":"r_ip","sortable":False,"editable":True},
            { "field": "r_int","title":"r_int","sortable":False},
            { "field": "l_ip_r_ip","title":"l_ip_r_ip","sortable":False},
            { "field": "util","title":"util","sortable":False},  
            { "field": "capacity","title":"capacity","sortable":False,"editable":True},
            { "field": "Action","title":"Action","formatter":"TableActions"},
            ]
    return render_template('model_demand.html',values=isis_links,columns=columns,router_name=router_name,netflow_demands=netflow_demands,
                           node_position=node_position)

@blueprint.route('/model_edit')
@login_required
def model_edit():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    #print 'node position ---------: {}'.format(node_position)
    netflow_demands = get_demand_netflow()
    #netflow_demands = [ {'source':'gb-p10-lon','target':'fr-p7-mrs','demand':1000000000} ]
    isis_links = {}
    #df.to_dict(orient='records')
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    router_name = df_router_name['anon_1'].values.tolist()
    #print isis_links
    columns = [
            { "field": "state","checkbox":True},
            { "field": "id","title":"id","sortable":False},
            { "field": "index","title":"index","sortable":False},
            { "field": "source","title":"source","sortable":True,"editable":True},
            { "field": "target","title":"target","sortable":False,"editable":True},
            { "field": "l_ip","title":"l_ip","sortable":False,"editable":True},
            { "field": "metric","title":"metric","sortable":False,"editable":True},
            { "field": "l_int","title":"l_int","sortable":False},
            { "field": "r_ip","title":"r_ip","sortable":False,"editable":True},
            { "field": "r_int","title":"r_int","sortable":False},
            { "field": "l_ip_r_ip","title":"l_ip_r_ip","sortable":False},
            { "field": "util","title":"util","sortable":False},  
            { "field": "capacity","title":"capacity","sortable":False,"editable":True},
	    { "field": "Action","title":"Action","formatter":"TableActions"},
            ]
    return render_template('model_edit.html',values=isis_links,columns=columns,router_name=router_name,netflow_demands=netflow_demands,
                           node_position=node_position)  
