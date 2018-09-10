from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint(
    'objects_blueprint', 
    __name__, 
    url_prefix = '/objects', 
    template_folder = 'templates',
    static_folder = 'static'
    )


from database import db
from .models import Routers,Prefixes,Links


@blueprint.route('/isis_prefixes')
@login_required
def isis_prefixes():
    isis_prefixes = Prefixes.query.all()
    return render_template('isis_prefixes.html', values=isis_prefixes)

@blueprint.route('/isis_routers')
@login_required
def isis_routers():
    isis_routers = Routers.query.all()
    return render_template('isis_routers.html', values=isis_routers)

@blueprint.route('/isis_links')
@login_required
def isis_links():
    isis_links = Links.query.all()
    return render_template('isis_links.html', values=isis_links)



