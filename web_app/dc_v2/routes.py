from flask import Blueprint, render_template, session
from flask_login import login_required
import pandas as pd
import json
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from database import db
from objects_v2.models import Fabric_links,Node_position


blueprint = Blueprint(
    'dc_blueprint',
    __name__,
    url_prefix = '/dc',
    template_folder = 'templates',
    static_folder = 'static'
    )

@blueprint.route('/dc_topology')
@login_required
def dc_topology():
    current_user = str(session['user_id'])
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user ).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')
    df = pd.read_sql(db.session.query(Fabric_links).filter(Fabric_links.index >=0).statement,db.session.bind)
    isis_links = df.to_dict(orient='records')
    return render_template('dc_topology.html', values=isis_links, node_position=node_position)

