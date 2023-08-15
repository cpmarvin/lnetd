from flask import Blueprint, render_template, session
from flask_login import login_required
import pandas as pd
import json
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from database import db
from objects_v2.models import Routers,Links,Node_position
from objects_v2.models import External_topology_temp,External_topology,External_position
from base_v2.basic_role import requires_roles

from .generate_data import generate_data
from .mutils import generat_unique_info, generate_traffic_util,get_month_util

from influxdb import InfluxDBClient
from datetime import date, timedelta

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
    current_user = session['_user_id']
    node_position = pd.read_sql(db.session.query(External_position).filter(External_position.user == current_user).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    df = pd.read_sql(db.session.query(External_topology).filter(External_topology.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    traffic_values = generate_traffic_util(df)
    return render_template(
                           'static_map.html',values=isis_links,
                                node_position=node_position,traffic_values=traffic_values)


@blueprint.route('/edit_static_map',methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def edit_static_map():
    current_user = session['_user_id']
    df = pd.read_sql(db.session.query(External_topology_temp).filter(External_topology_temp.index >=0).statement,db.session
.bind)
    isis_links = df.to_dict(orient='records')# External_topology_temp
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    router_name = df_router_name['source'].values.tolist()
    return render_template('edit_static_map.html',values=isis_links,router_name=router_name)



@blueprint.route('/peer_report')
@login_required
def peer_report():
    objects_counters = generat_unique_info()
    objects_counters = sorted(objects_counters , key = lambda i: i['index'])
    #print(objects_counters)
    return render_template('peer_report.html',objects_counters=objects_counters)


@blueprint.route('/get_graph_data_interface',methods=['GET', 'POST'])
@login_required
def get_graph_data_interface():
    INFLUXDB_NAME = 'telegraf'
    client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)
    rvalue = request.args
    if rvalue['time'] == '24h':
        query = f"""select non_negative_derivative(last(ifHCOutOctets), 1s) *8  as bps_out , non_negative_derivative(last(ifHCInOctets), 1s) *8 as bps_in , last(ifHighSpeed) as capacity
		from interface_statistics where hostname =~/{rvalue['router']}/ and ifName ='{rvalue['interface']}' 
		AND time >= now()- 24h and time < now()
                GROUP BY time(5m) """
    else:
        query = f"""select non_negative_derivative(last(ifHCOutOctets), 1s) *8  as bps_out , non_negative_derivative(last(ifHCInOctets), 1s) *8 as bps_in , last(ifHighSpeed) as capacity
                from interface_statistics where hostname =~/{rvalue['router']}/ and ifName ='{rvalue['interface']}'
                AND time >= now()- 365d and time < now()
                GROUP BY time(1h) """
    #print(query)
    result = client.query(query)
    t = list(result.get_points(measurement='interface_statistics'))
    df = pd.DataFrame(t)
    if df.empty:
        return "status error", "400 No SNMP data for this router and interface"
    #jsonify('No data found'),400 
    df['name'] = rvalue['interface']
    df = df.fillna(0)
    result = df.reindex(columns=["time","bps_in","bps_out","name","capacity"]).to_dict(orient='records')
    #print('888888888888888------',query,result,df)
    return jsonify(result)

@blueprint.route('/get_graph_data',methods=['GET', 'POST'])
@login_required
def get_graph_data():
    rvalue = request.args
    if rvalue['type'] != '':
        query = f'''select sum(cir) as cir, sum(capacity) as capacity, sum(bps_out) as bps_out ,sum(bps_in) as bps_in from h_transit_statistics where country =~/{rvalue['country']}/
        and pop =~/{rvalue['pop']}/
        and type =~ /{rvalue['type']}/
        AND time >= now()- 7d and time < now()
                        GROUP BY time(1h)'''
    else:
        query = f'''select sum(cir) as cir, sum(capacity) as capacity, sum(bps_out) as bps_out ,sum(bps_in) as bps_in from h_transit_statistics where country =~/{rvalue['country']}/
        and pop =~/{rvalue['pop']}/
        and target =~ /{rvalue['target']}/
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
