from flask import Blueprint, render_template, session, Response
from flask_login import login_required
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from database import db
from objects.models import bgp_groups
import pandas as pd
import json
import sys
sys.path.append('./prov/mutils')
from deploy_nornir import nornir_config
from generate_template import nornir_template

blueprint = Blueprint(
    'prov_blueprint',
    __name__,
    url_prefix='/prov',
    template_folder='templates',
    static_folder='static'
)


def _test_print(object):
    for host, host_data in object.items():
        title = (
            ""
            if host_data.changed is None
            else " ** changed : {} ".format(host_data.changed)
        )
        msg = "* {}{}".format(host, title)
        result1 = host_data[0].result
        result2 = host_data[0].diff
        result3 = host_data[0].stdout
        if host_data.failed:
            return "Device:{} Failed with the following exception\nResult:\n{}".format(msg, result1)
        if host_data.changed == False:
            return "Device:{} \nThe configuration was already on the device so no change".format(msg)
        return "Device:{} Configured correctly\nDiff:\n{}".format(msg, result2)


@blueprint.route('/peering_prov', methods=['GET', 'POST'])
@login_required
def peering_prov():
    df = pd.read_sql(db.session.query(bgp_groups).filter(
        bgp_groups.index >= 0).statement, db.session.bind)
    result = df.groupby('router')['group'].apply(list).to_dict()
    return render_template(
        'peering_prov.html', values=result)


@blueprint.route('/generate_config', methods=['GET', 'POST'])
@login_required
def generate_config():
    config_router = request.args['router']
    config_ip = request.args['ip']
    config_asn = request.args['asn']
    config_peer_group = request.args['peer_group']
    variable = {'ip': config_ip, 'asn': config_asn,
                'router': config_router, 'peer_group': config_peer_group}
    nornir_result = nornir_template(variable, config_router)
    if nornir_result['status'] == 'OK':
        return jsonify(nornir_result['result']), 200, {'ContentType': 'application/json'}
    return jsonify(nornir_result['result']), 201, {'ContentType': 'application/json'}


@blueprint.route('/deploy_config', methods=['GET', 'POST'])
@login_required
def deploy_config():
    router = request.args['router']
    config = request.args['config']
    nornir_result = nornir_config(router, config)
    return jsonify(_test_print(nornir_result))
    #return jsonify('this is just a demo site :) check github for deployment code ')
