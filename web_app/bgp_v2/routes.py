from flask import Blueprint, render_template, session
from flask_login import login_required
from database import db
from objects_v2.models import Bgp_peers, Bgp_peering_points,Node_position_global
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

