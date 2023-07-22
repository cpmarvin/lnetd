from flask import Blueprint, render_template
from flask_login import login_required

from objects_v2.models import Routers, Prefixes, Links

from collections import Counter, OrderedDict
from database import db
from base_v2.models import User

from objects_v2.models import Tag,Tacacs

from .properties import pretty_names

import pandas as pd

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
        'prefixes_v4': len(Prefixes.query.filter_by(version = '4').all()),
        'prefixes_v6': len(Prefixes.query.filter_by(version = '6').all()),
        'users': len(User.query.all()),
    }
    # get counters for routers
    routers = Routers.query.all()
    prefixes = Prefixes.query.all()
    links = Links.query.all()
    prefix_total_count = Counter(k.name for k in prefixes)
    prefix_top10_count = Counter(dict(prefix_total_count.most_common(5)))
    links_total_count = Counter(k.source for k in links)
    links_top10_count = Counter(dict(links_total_count.most_common(5)))
    objects_counters = {"ARouter_per_country": Counter(k.country for k in routers),
                        "BPrefix_per_country": Counter(k.country for k in prefixes),
                        "CPrefix_per_router": prefix_top10_count,
                        "DLinks_per_router": links_top10_count,
  			             "network_vendors": Counter(k.vendor for k in routers)
                        }
    tag_values = pd.read_sql(db.session.query(Tag).statement,db.session.bind)
    tag_values['text'] = tag_values['name']
    tag_values['id'] = tag_values['name']
    tag_values = tag_values.to_dict(orient='records')
    tacacs_id = Tacacs.query.all()

    return render_template('index.html', objects_counters=objects_counters, 
			counters=counters, names=pretty_names,routers=routers,tag_values=tag_values,
			tacacs_id=tacacs_id,links=links,prefixes=prefixes)

@blueprint.route('/support')
@login_required
def support():
    return render_template('support.html')
