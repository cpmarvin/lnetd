from flask import Blueprint, render_template, session
from flask_login import login_required
from database import db
from objects_v2.models import Bgp_peers, Bgp_customers, Bgp_peering_points,Node_position_global
from base_v2.basic_role import requires_roles

import pandas as pd

from .mutils import generate_peer_map

blueprint = Blueprint(
    'bgp_blueprint',
    __name__,
    url_prefix='/bgp',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/bgp_customers')
@login_required
def bgp_customers():
    isis_prefixes = Bgp_customers.query.all()
    return render_template('bgp_customers.html', values=isis_prefixes)


@blueprint.route('/bgp_peers')
@login_required
def bgp_peers():
    isis_prefixes = Bgp_peers.query.all()
    return render_template('bgp_peers.html', values=isis_prefixes)

@blueprint.route('/bgp_map')
@login_required
def bgp_map():
    current_user = session['_user_id']
    node_position = pd.read_sql(db.session.query(Node_position_global).filter(
        Node_position_global.user == current_user).filter(Node_position_global.map_type == 'bgp').statement, db.session.bind)
    node_position = node_position.to_dict(orient='records')
    df_map = generate_peer_map()
    bgp_map = df_map[0].to_dict(orient='records')
    ibgp_map = df_map[1].to_dict(orient='records')
    return render_template('bgp_map.html', values=bgp_map, ibgp_values=ibgp_map, node_position=node_position)

@blueprint.route('/edit_peering_points')
@login_required
@requires_roles('admin')
def edit_peering_points():
    df = pd.read_sql(db.session.query(Bgp_peering_points).filter(
        Bgp_peering_points.index >= 0).statement, db.session.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')
    columns = [
        {"field": "state", "checkbox": True},
        {"field": "id", "title": "id", "sortable": False,"class":"hide_me"},
        {"field": "index", "title": "index", "sortable": False,"class":"hide_me"},
        {"field": "name", "title": "name", "sortable": True, "editable": True},
        {"field": "ipv4", "title": "ipv4", "sortable": False, "editable": True},
        {"field": "ipv6", "title": "ipv6", "sortable": False, "editable": True},
        {"field": "Action", "title": "Action", "formatter": "TableActions"},
    ]
    return render_template('edit_peering_points.html', values=isis_links, columns=columns)
