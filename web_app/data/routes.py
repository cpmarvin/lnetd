from flask import Blueprint, render_template, request
from flask_login import login_required
from objects.models import Routers,Links
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
    print isis_links 
    return render_template('topology.html', values=isis_links)


@blueprint.route('/filter_topology',methods=['GET', 'POST'])
@login_required
def filter_topology():
    source_filter = request.form.get('source_filter')
    target_filter = request.form.get('source_filter')
    print source_filter
    df = pd.read_sql(db.session.query(Links).filter(Links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return render_template('filter_topology.html',values=isis_links,source_filter = source_filter,target_filter=target_filter)

