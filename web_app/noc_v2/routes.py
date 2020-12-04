from flask import Blueprint, render_template, request, session
from flask_login import login_required

from objects_v2.models import (
    Routers,
    Links,
    Links_latency,
    Node_position,
    App_config,
    Noc_Topology_Edit,
    Noc_Topology,
    Node_position_global,
)
from database import db
from collections import Counter, OrderedDict
import pandas as pd


import json

from influxdb import InfluxDBClient
from sqlalchemy import or_, and_

from .mutils import *

import collections
from functools import reduce

blueprint = Blueprint(
    "noc_blueprint",
    __name__,
    url_prefix="/noc",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/edit_topology")
@login_required
def edit_topology():
    current_user = str(session["_user_id"])
    df_router_name = pd.read_sql(
        db.session.query(Links.source.distinct()).statement, db.session.bind
    )
    router_name = df_router_name["anon_1"].values.tolist()

    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    df = pd.read_sql(
        db.session.query(Noc_Topology_Edit).filter(Noc_Topology_Edit.id >= 0).statement,
        db.session.bind,
    )
    noc_links = df.to_dict(orient="records")
    # layer1_links = Layer1Topology.query.all()
    igp_links_df = generate_from_igp()
    igp_links = igp_links_df.to_dict(orient="records")
    return render_template(
        "edit_topology.html",
        noc_links=noc_links,
        igp_links=igp_links,
        router_name=router_name,
    )


@blueprint.route("/core_dashboard")
@login_required
def core_dashboard():
    return render_template("core_dashboard.html")


@blueprint.route("/noc_topology")
@login_required
def noc_topology():
    current_user = str(session["_user_id"])
    node_position = pd.read_sql(
        db.session.query(Node_position_global)
        .filter(Node_position_global.user == current_user)
        .filter(Node_position_global.map_type == "noc")
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    df = pd.read_sql(
        db.session.query(Noc_Topology).filter(Noc_Topology.id >= 0).statement,
        db.session.bind,
    )
    noc_links = df.to_dict(orient="records")
    return render_template(
        "noc_topology.html", values=noc_links, node_position=node_position
    )


@blueprint.route("/save_noc_topology", methods=["POST"])
@login_required
def save_noc_topology():
    arr = request.args["arr"]
    df = pd.DataFrame(eval(arr))
    print(df)
    df.to_sql(name="Noc_Topology_Edit", con=db.engine, index=False, if_exists="replace")
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
