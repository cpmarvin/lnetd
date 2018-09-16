from flask import Blueprint, render_template, request
from flask_login import login_required
from objects.models import Routers,Links,Links_latency
from database import db
from collections import Counter,OrderedDict
import pandas as pd

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
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    #print isis_links 
    return render_template('topology.html', values=isis_links)

@blueprint.route('/topology_errors')
@login_required
def topology_errors():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    #print isis_links
    return render_template('topology_errors.html', values=isis_links)

@blueprint.route('/topology_latency')
@login_required
def topology_latency():
    df = pd.read_sql(db.session.query(Links_latency).filter(Links_latency.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    #print isis_links
    return render_template('topology_latency.html', values=isis_links)

@blueprint.route('/filter_topology',methods=['GET', 'POST'])
@login_required
def filter_topology():
    source_filter = request.form.get('source_filter')
    target_filter = request.form.get('source_filter')
    #print source_filter
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return render_template('filter_topology.html',values=isis_links,source_filter = source_filter,target_filter=target_filter)


@blueprint.route('/model_isis_links', methods=['GET', 'POST'])
@login_required
def model_isis_links():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    print isis_links
    columns = [
            { "field": "index","title":"index","sortable":False},
            { "field": "source","title":"source","sortable":True},
            { "field": "target","title":"target","sortable":False},
            { "field": "l_ip","title":"l_ip","sortable":False},
            { "field": "metric","title":"metric","sortable":False,"editable":True},
            { "field": "l_int","title":"l_int","sortable":False},
            { "field": "r_ip","title":"r_ip","sortable":False},
            { "field": "r_int","title":"r_int","sortable":False},
            { "field": "l_ip_r_ip","title":"l_ip_r_ip","sortable":False},
            { "field": "util","title":"util","sortable":False},
            { "field": "capacity","title":"capacity","sortable":False}
            ]
    return render_template('model_isis_links.html',values=isis_links,columns=columns)

@blueprint.route('/model_demand', methods=['GET', 'POST'])
@login_required
def model_demand():
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    df['util'] = -1
    isis_links = df.to_dict(orient='records')
    #print isis_links
    columns = [
            { "field": "index","title":"index","sortable":False},
            { "field": "source","title":"source","sortable":True},
            { "field": "target","title":"target","sortable":False},
            { "field": "l_ip","title":"l_ip","sortable":False},
            { "field": "metric","title":"metric","sortable":False,"editable":True},
            { "field": "l_int","title":"l_int","sortable":False},
            { "field": "r_ip","title":"r_ip","sortable":False},
            { "field": "r_int","title":"r_int","sortable":False},
            { "field": "l_ip_r_ip","title":"l_ip_r_ip","sortable":False},
            { "field": "util","title":"util","sortable":False},
            { "field": "capacity","title":"capacity","sortable":False}
            ]
    return render_template('model_demand.html',values=isis_links,columns=columns)

