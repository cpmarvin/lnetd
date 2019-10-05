from flask import Blueprint, render_template
from flask_login import login_required
from objects.models import Routers, Prefixes, Links
from collections import Counter, OrderedDict
from database import db
from base.models import User
from .properties import pretty_names

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='/home',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/index')
@login_required
def index():
    counters = {
        'routers': len(Routers.query.all()),
        'links': int(len(Links.query.all()) / 2),
        'prefixes': len(Prefixes.query.all()),
        'users': len(User.query.all())
    }
    # get counters for routers
    routers = Routers.query.all()
    prefixes = Prefixes.query.all()
    links = Links.query.all()
    prefix_total_count = Counter(k.name for k in prefixes)
    prefix_top10_count = Counter(dict(prefix_total_count.most_common(10)))
    links_total_count = Counter(k.source for k in links)
    links_top10_count = Counter(dict(links_total_count.most_common(10)))
    objects_counters = {"ARouter_per_country": Counter(k.country for k in routers),
                        "BPrefix_per_country": Counter(k.country for k in prefixes),
                        "CPrefix_per_router": prefix_top10_count,
                        "DLinks_per_router": links_top10_count
                        }
    return render_template('index.html', objects_counters=objects_counters, counters=counters, names=pretty_names)
