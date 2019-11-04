from flask import Blueprint, render_template, session
from flask_login import login_required
import pandas as pd
import json
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from database import db
from objects.models import Routers,Links,Links_latency,Node_position
from objects.models import External_topology_temp,External_topology,External_position
from objects.models import International_PoP,International_PoP_temp
from objects.models import App_external_flows

from .generate_data import generate_data
from .mutils import generat_unique_info, generate_traffic_util

from influxdb import InfluxDBClient
INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf_agg'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)

blueprint = Blueprint(
    'map_blueprint', 
    __name__, 
    url_prefix = '/map', 
    template_folder = 'templates',
    static_folder = 'static'
    )

@blueprint.route('/static_map',methods=['GET', 'POST'])
@login_required
def static_map():
    current_user = session['user_id']
    node_position = pd.read_sql(db.session.query(External_position).filter(External_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    #source_filter = request.form.get('source_filter')
    #target_filter = request.form.get('source_filter')
    #print source_filter
    df = pd.read_sql(db.session.query(External_topology).filter(External_topology.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    traffic_values = generate_traffic_util(df)
    return render_template(
                           'static_map.html',values=isis_links,
                                node_position=node_position,traffic_values=traffic_values)

@blueprint.route('/edit_static_map',methods=['GET', 'POST'])
@login_required
def edit_static_map():
    current_user = session['user_id']
    df = pd.read_sql(db.session.query(External_topology_temp).filter(External_topology_temp.index >=0).statement,db.session
.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')# External_topology_temp
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    router_name = df_router_name['anon_1'].values.tolist()
    columns = [
            { "field": "state","checkbox":True },
            { "field": "id","title":"id","sortable":False,"class":"hide_me"},
            { "field": "index","title":"index","sortable":False,"class":"hide_me"},
            { "field": "source","title":"source","sortable":True,"editable":True},
            { "field": "target","title":"target","sortable":False,"editable":True},
            { "field": "node","title":"node","sortable":False,"editable":True},
            { "field": "interface","title":"interface","sortable":False,"editable":True},
            { "field": "direction","title":"direction","sortable":False,"editable":True},
            { "field": "src_icon","title":"src_icon","sortable":False,"editable":True,"class":"hide_me"},
            { "field": "tar_icon","title":"tar_icon","sortable":False,"editable":True,"class":"hide_me"},
            { "field": "cir","title":"cir","sortable":False,"editable":True},
            { "field": "type","title":"type","sortable":False,"editable":True},
            { "field": "Action","title":"Action","formatter":"TableActions"},
            ]
    return render_template('edit_static_map.html',values=isis_links,columns=columns,router_name=router_name)

@blueprint.route('/external_flow',methods=['GET', 'POST'])
@login_required
def external_flow():
    peer = request.form.get('peer')
    if peer:
        df = pd.read_sql(db.session.query(App_external_flows).filter(App_external_flows.name == peer).statement,db.session.bind)
        transit = df.to_dict(orient='records')
        name = transit[0]['name']
        router_ip = transit[0]['router']
        ifindex = transit[0]['if_index']
        #print('found a peer------------------------',peer,name,router_ip,ifindex)
    else:
        peer = 'AMSIX'
        name = 'AMSIX'
        router_ip = '10.3.3.3'
        ifindex = '68'
        #print(peer,name,router_ip,ifindex)
    diagram = generate_data(name,router_ip,ifindex)
    app_netflow_config = App_external_flows.query.all()
    return render_template('external_flow.html', values=diagram,peer=peer,app_netflow_config=app_netflow_config)


@blueprint.route('/edit_international_pop',methods=['GET', 'POST'])
@login_required
def edit_internation_pop():
    df = pd.read_sql(db.session.query(International_PoP_temp).filter(International_PoP_temp.index >=0).statement,db.session.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')# External_topology_temp
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    columns = [
            { "field": "state","checkbox":True },
            { "field": "id","title":"id","sortable":False,"class":"hide_me"},
            { "field": "index","title":"index","sortable":False,"class":"hide_me"},
            { "field": "name","title":"name","sortable":True,"editable":True},
            { "field": "routers","title":"routers","sortable":False,"editable":True},
            { "field": "region","title":"region","sortable":False,"editable":True},
            { "field": "lat","title":"lat","sortable":False,"editable":True},
            { "field": "lon","title":"lon","sortable":False,"editable":True},
            { "field": "Action","title":"Action","formatter":"TableActions"},
            ]
    return render_template('edit_international_pop.html',values=isis_links,columns=columns)

@blueprint.route('/international_pop')
@login_required
def internation_pop():
    internation_pop = International_PoP.query.all()
    qry = db.session.query(International_PoP).filter(International_PoP.region.like('EA')).statement
    df_ea = pd.read_sql(qry,db.session.bind)
    df_ea = df_ea.to_dict(orient='records')
    qry = db.session.query(International_PoP).filter(International_PoP.region.like('SA')).statement
    df_sa = pd.read_sql(qry,db.session.bind)
    df_sa = df_sa.to_dict(orient='records')
    qry = db.session.query(International_PoP).filter(International_PoP.region.like('EU')).statement
    df_eu = pd.read_sql(qry,db.session.bind)
    df_eu = df_eu.to_dict(orient='records')
    return render_template('international_pop.html', values=internation_pop,df_ea=df_ea,df_sa=df_sa,df_eu=df_eu)

@blueprint.route('/peer_report')
@login_required
def peer_report():
    objects_counters = generat_unique_info()
    objects_counters = sorted(objects_counters , key = lambda i: i['index'])
    #print(objects_counters)
    return render_template('peer_report.html',objects_counters=objects_counters)

@blueprint.route('/get_graph_data',methods=['GET', 'POST'])
@login_required
def get_graph_data():
    rvalue = request.args
    if rvalue['type'] != '':
        query = f'''select sum(cir) as cir, sum(capacity) as capacity, max(bps_out) as bps_out ,max(bps_in) as bps_in from h_transit_statistics where country =~/{rvalue['country']}/
        and pop =~/{rvalue['pop']}/
        and type =~ /{rvalue['type']}/
        AND time >= now()- 7d and time < now()
                        GROUP BY time(1h)'''
    else:
        query = f'''select sum(cir) as cir, sum(capacity) as capacity, max(bps_out) as bps_out ,max(bps_in) as bps_in from h_transit_statistics where country =~/{rvalue['country']}/
        and pop =~/{rvalue['pop']}/
        and type =~ /{rvalue['type']}/
        AND time >= now()- 7d and time < now()
                        GROUP BY time(1h)'''
    result = client.query(query)
    t = list(result.get_points(measurement='h_transit_statistics'))
    df = pd.DataFrame(t)
    df = df.fillna(0)
    df['div_id'] = rvalue['index']
    df['name'] = rvalue['name']
    df['cir'] = df['cir'] * 1000000
    df['capacity'] = df['capacity'] * 1000000
    result = df.reindex(columns=["time","bps_in","bps_out","div_id","name","cir","capacity"]).to_dict(orient='records')
    #print(df)
    return jsonify(result)
