from flask import Blueprint, render_template
from flask_login import login_required
from .properties import pretty_names

blueprint = Blueprint(
    'objects_blueprint',
    __name__,
    url_prefix='/objects',
    template_folder='templates',
    static_folder='static'
)


from database import db
from .models import Routers, Prefixes, Links, Tacacs, Tag


@blueprint.route('/isis_prefixes')
@login_required
def isis_prefixes():
    isis_prefixes = Prefixes.query.all()
    return render_template('isis_prefixes.html', values=isis_prefixes)

@blueprint.route('/isis_routers')
@login_required
def isis_routers():
    isis_routers = Routers.query.all()
    tacacs_id = Tacacs.query.all()
    tag_values = Tag.query.all()
    import pandas as pd
    tag_values = pd.read_sql(db.session.query(Tag).statement,db.session.bind)
    tag_values['text'] = tag_values['name']
    tag_values['id'] = tag_values['name']
    tag_values = tag_values.to_dict(orient='records')
    return render_template('isis_routers.html', values=isis_routers, names=pretty_names, tacacs_id=tacacs_id,tag_values = tag_values)

@blueprint.route('/isis_links')
@login_required
def isis_links():
    isis_links = Links.query.all()
    return render_template('isis_links.html', values=isis_links)
