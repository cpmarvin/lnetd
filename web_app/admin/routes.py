from flask import Blueprint, render_template, request
from flask_login import login_required
from base.basic_role import requires_roles

from database import db
from objects.models import App_config, App_external_flows, Tacacs, Routers, Tag
from base.models import User

import pandas as pd
import json

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='/admin',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/app_config')
@login_required
@requires_roles('admin')
def app_config():
    app_config_current = App_config.query.all()
    asn = app_config_current[0].asn
    web_ip = app_config_current[0].web_ip
    influx_ip = app_config_current[0].influx_ip
    nb_url = app_config_current[0].nb_url
    nb_token = app_config_current[0].nb_token
    master_key = app_config_current[0].master_key
    return render_template('app_config.html', asn=asn, web_ip=web_ip, influx_ip=influx_ip, nb_url=nb_url, nb_token=nb_token, master_key=master_key)


@blueprint.route('/app_config_save', methods=['POST'])
@login_required
@requires_roles('admin')
def app_config_save():
    try:
        app_new_conf = App_config(**request.form)
        App_config.query.delete()
        db.session.merge(app_new_conf)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}


@blueprint.route('/app_add_user', methods=['POST'])
@login_required
@requires_roles('admin')
def app_add_user():
    try:
        app_add_user = User(**request.form)
        db.session.merge(app_add_user)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print(e)
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}


@blueprint.route('/app_new_user')
@login_required
@requires_roles('admin')
def app_new_user():
    users_list = User.query.all()
    return render_template('app_new_user.html', values=users_list)


@blueprint.route('/app_external_netflow')
@login_required
@requires_roles('admin')
def app_external_netflow():
    df = pd.read_sql(db.session.query(App_external_flows).filter(
        App_external_flows.index >= 0).statement, db.session.bind)
    df['id'] = df['index']
    isis_links = df.to_dict(orient='records')
    columns = [
        {"field": "state", "checkbox": True},
        {"field": "id", "title": "id", "sortable": False,"class":"hide_me"},
        {"field": "index", "title": "index", "sortable": False,"class":"hide_me"},
        {"field": "name", "title": "name", "sortable": True, "editable": True},
        {"field": "router", "title": "router",
            "sortable": False, "editable": True},
        {"field": "if_index", "title": "if_index",
            "sortable": False, "editable": True},
        {"field": "Action", "title": "Action", "formatter": "TableActions"},
    ]
    return render_template('app_external_netflow.html', values=isis_links, columns=columns)


@blueprint.route('/app_external_netflow_save', methods=['POST'])
@login_required
@requires_roles('admin')
def app_external_netflow_save():
    try:
        arr = request.args['arr']
        df = pd.DataFrame(eval(arr))
        df = df.drop(['', 'index', 'Action', 'id'], axis=1)
        df.to_sql(name='App_external_flows',
                  con=db.engine, if_exists='replace')
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print(e)
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}


def handle_tags(router_name=None,tags=None):
    try:
        router = Routers.query.filter_by(name=str(router_name)).first()
        #delete all tags on existing router (not safe)
        router.tags = []
        all_tags = Tag.query.all()
        all_tags_list = [ tag.name for tag in all_tags ]
        for tag in tags:
            if tag == 'null':
                return
            #if its a new tag , add it to tag table
            if tag not in all_tags_list:
                entry_tag = Tag(name=tag)
                db.session.merge(entry_tag)
                db.session.commit()
            tag_current = Tag.query.filter_by(name=str(tag)).first()
            router.tags.append(tag_current)
    except Exception as e:
        raise Exception('Error in handle_tags')

@blueprint.route('/app_edit_router', methods=['POST'])
@login_required
@requires_roles('admin')
def app_edit_router():
    try:
        app_add_tacacs = request.form.to_dict()
        all_tags = app_add_tacacs['all_tags'].split(',')
        router_name = app_add_tacacs['router_name']
        tacacs_id = int(app_add_tacacs['tacacs'])
        router = Routers.query.filter_by(name=router_name).first()
        router.tacacs_id = tacacs_id
        #take care of tags for this router
        handle_tags(router,all_tags)
        db.session.merge(router)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        return 'e'


@blueprint.route('/app_add_tacacs', methods=['POST'])
@login_required
@requires_roles('admin')
def app_add_tacacs():
    try:
        app_config = App_config.query.all()
        master_key = app_config[0].master_key
        app_add_tacacs = Tacacs(master_key, **request.form)
        db.session.merge(app_add_tacacs)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print(e)
        return 'e'


@blueprint.route('/app_new_tacacs')
@login_required
@requires_roles('admin')
def app_new_tacacs():
    lnetd_tacacs = Tacacs.query.all()
    return render_template('app_new_tacacs.html', values=lnetd_tacacs)


@blueprint.route('/delete_object', methods=['POST', 'GET'])
@login_required
@requires_roles('admin')
def delete_object():
    type = request.args['type']
    id = int(request.args['id'])
    if type == 'Tacacs':
        delete_object = db.session.query(Tacacs).get(id)
    elif type == 'Users':
        delete_object = db.session.query(User).get(id)
    db.session.delete(delete_object)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
