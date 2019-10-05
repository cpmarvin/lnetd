from flask import Blueprint, render_template
from flask_login import login_required
from database import db
from objects.models import Bgp_peers, Bgp_customers, Bgp_peering_points
import pandas as pd

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


@blueprint.route('/edit_peering_points')
@login_required
def edit_peering_points():
    df = pd.read_sql(db.session.query(Bgp_peering_points).filter(
        Bgp_peering_points.index >= 0).statement, db.session.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')
    columns = [
        {"field": "state", "checkbox": True},
        {"field": "id", "title": "id", "sortable": False},
        {"field": "index", "title": "index", "sortable": False},
        {"field": "name", "title": "name", "sortable": True, "editable": True},
        {"field": "ipv4", "title": "ipv4", "sortable": False, "editable": True},
        {"field": "ipv6", "title": "ipv6", "sortable": False, "editable": True},
        {"field": "Action", "title": "Action", "formatter": "TableActions"},
    ]
    return render_template('edit_peering_points.html', values=isis_links, columns=columns)
