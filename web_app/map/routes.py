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
from .generate_data import generate_data

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
    source_filter = request.form.get('source_filter')
    target_filter = request.form.get('source_filter')
    #print source_filter
    df = pd.read_sql(db.session.query(External_topology).filter(External_topology.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    df_inbound_total = df.loc[df['direction'] == 'in']
    df_inbound_transit = df_inbound_total.loc[df['source'].str.contains(r'(TRANS)')]
    df_inbound_cdn = df_inbound_total.loc[df['source'].str.contains(r'(CDN)')]
    total_inbound = df_inbound_total['util'].sum()
    total_transit = df_inbound_transit['util'].sum()
    total_cdn = df_inbound_cdn['util'].sum()
    total_peering = total_inbound - total_transit - total_cdn
    return render_template(
                           'static_map.html',values=isis_links,source_filter = source_filter,target_filter=target_filter,
                                node_position=node_position,total_inbound=total_inbound,total_transit=total_transit,
                                total_peering=total_peering,total_cdn=total_cdn
                          )

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
            { "field": "id","title":"id","sortable":False},
            { "field": "index","title":"index","sortable":False},
            { "field": "source","title":"source","sortable":True,"editable":True},
            { "field": "target","title":"target","sortable":False,"editable":True},
            { "field": "node","title":"node","sortable":False,"editable":True},
            { "field": "interface","title":"interface","sortable":False,"editable":True},
            { "field": "direction","title":"direction","sortable":False,"editable":True},
            { "field": "src_icon","title":"src_icon","sortable":False,"editable":True},
            { "field": "tar_icon","title":"tar_icon","sortable":False,"editable":True},
            { "field": "Action","title":"Action","formatter":"TableActions"},
            ]
    return render_template('edit_static_map.html',values=isis_links,columns=columns,router_name=router_name)

@blueprint.route('/external_flow',methods=['GET', 'POST'])
@login_required
def external_flow():
    transit = {
         'AMSIX':{'router_ip':'10.3.3.3','interface':'68'},
        }
    peer = request.form.get('peer')
    if peer:
        name = peer
        router_ip = transit[peer]['router_ip']
        ifindex = transit[peer]['interface']
        print('found a peer',peer,name,router_ip,ifindex)
    else:
        peer = 'AMSIX'
        name = 'AMSIX'
        router_ip = '10.3.3.3'
        ifindex = '68'
        print(peer,name,router_ip,ifindex)
    diagram = generate_data(name,router_ip,ifindex)
    return render_template('external_flow.html', values=diagram,peer=peer)


@blueprint.route('/edit_international_pop',methods=['GET', 'POST'])
@login_required
def edit_internation_pop():
    df = pd.read_sql(db.session.query(International_PoP_temp).filter(International_PoP_temp.index >=0).statement,db.session.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')# External_topology_temp
    df_router_name = pd.read_sql(db.session.query(Links.source.distinct()).statement,db.session.bind)
    columns = [
            { "field": "state","checkbox":True },
            { "field": "id","title":"id","sortable":False},
            { "field": "index","title":"index","sortable":False},
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
