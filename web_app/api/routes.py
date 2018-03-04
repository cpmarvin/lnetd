from flask import Blueprint, render_template, request
from flask_login import login_required
from collections import Counter,OrderedDict
import pandas as pd

from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from get_graph_fct_ifindex import get_graph_ifindex
from get_interface_ifName_fct import get_interface_ifName
from calculateSfp_fct import calculateSfp

blueprint = Blueprint(
    'api_blueprint', 
    __name__, 
    url_prefix = '/api', 
    template_folder = 'templates',
    static_folder = 'static'
    )

@blueprint.route('/ifName',methods=['GET', 'POST'])
@login_required
def ifName():
    ip = request.args['ip']
    host = request.args['host']
    print "interface: %s , host : %s " %(ip,host)
    results = get_interface_ifName(host,ip)
    print "--------------------AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA----------------%s" %results
    return results

@blueprint.route('/graph_ifindex')
@login_required
def graph():
    ip = request.args['ip']
    host = request.args['host']
    print "interface: %s , host : %s " %(ip,host)
    results = get_graph_ifindex(host,ip)
    return results

@blueprint.route('/spf')
@login_required
def sfp():
    source = request.args['source']
    target = request.args['target']
    arr = request.args['arr']
    results = calculateSfp(arr,source,target)
    print "results: %s" %jsonify(results)
    return jsonify(results)
