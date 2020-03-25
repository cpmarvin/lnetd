from flask import Blueprint, render_template, request, session
from flask_login import login_required
from base_v2.basic_role import requires_roles

from database import db
from objects_v2.models import App_config, App_external_flows, Tacacs, Routers, Tag,Links, Node_position
from base_v2.models import User

import pandas as pd
import json

from .mutils import generate_network_report

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='/admin',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/admin_report_failed', methods=['POST','GET'])
@login_required
#@requires_roles('admin')
def admin_report_failed():
    rvalue = request
    rvalue_dict = rvalue.args.to_dict(flat=False)
    type = rvalue_dict['type'][0]
    failed_links = json.loads(rvalue_dict['links'][0])

    current_user = str(session['_user_id'])
    node_position = pd.read_sql(db.session.query(Node_position).filter(Node_position.user == current_user ).statement,db.session.bind)
    node_position = node_position.to_dict(orient='records')

    df = pd.read_sql(db.session.query(Links).statement,db.session.bind)
    df['status']='up'
    network_initial = df.to_dict(orient='records')

    #failed_links = ['10.2.3.2','10.22.33.22']
    df_failed = pd.read_sql(db.session.query(Links).statement,db.session.bind)
    df_failed['status']='up'
    df_failed.loc[ (df_failed['l_ip'].isin(failed_links)) | (df_failed['r_ip'].isin(failed_links)) , 'status'] = 'down'
    network_failed = df_failed.to_dict(orient='records')

    network_report = generate_network_report(initial_network=df,failed_network=df_failed,compare=True)
    initial_netowrk_paths = pd.DataFrame(network_report['initial_network']['paths'])
    failed_network_paths = pd.DataFrame(network_report['failed_network']['paths'])
    change_paths_df = initial_netowrk_paths.merge(failed_network_paths, suffixes=['_initial','_failed'],indicator=True, how='outer' , on=['source','target'])
    print(change_paths_df)
    change_paths = change_paths_df.to_dict(orient='records')

    return render_template('admin_report_failed.html',network_report=network_report,change_paths=change_paths,
		network_initial=network_initial, network_failed=network_failed,node_position=node_position)

@blueprint.route('/admin_report')
@login_required
#@requires_roles('admin')
def admin_report():
    df = pd.read_sql(db.session.query(Links).statement,db.session.bind)
    df['status']='up'
    network_report = generate_network_report(initial_network=df,failed_network=None,compare=False)
    print(network_report)
    return render_template('admin_report.html',network_report=network_report)

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
    users_list = User.query.all()
    lnetd_tacacs = Tacacs.query.all()
    alert_threshold = app_config_current[0].alert_threshold
    alert_backoff = app_config_current[0].alert_backoff
    return render_template('app_config.html', asn=asn, web_ip=web_ip, 
		influx_ip=influx_ip, nb_url=nb_url, nb_token=nb_token, master_key=master_key,users_list=users_list,lnetd_tacacs=lnetd_tacacs,alert_threshold=alert_threshold,
		alert_backoff=alert_backoff)


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
        return json.dumps({'error': False}), 400, {'ContentType': 'application/json'}


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

@blueprint.route('/app_edit_routers', methods=['POST'])
@login_required
@requires_roles('admin')
def app_edit_routers():
    try:
        app_add_tacacs = request.form.to_dict()
        print(app_add_tacacs)
        all_tags = app_add_tacacs['all_tags'].split(',')
        all_routers = app_add_tacacs['routers'].split(',')
        tacacs_id = int(app_add_tacacs['tacacs'])
        for entry in all_routers:
            print(entry)
            router = Routers.query.filter_by(name=entry).first()
            router.tacacs_id = tacacs_id
            #take care of tags for this router
            handle_tags(router,all_tags)
            db.session.merge(router)
            db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print('error',e)
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
