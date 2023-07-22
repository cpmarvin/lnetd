from flask import Blueprint, render_template, request, session
from flask_login import login_required
from objects_v2.models import (
    Routers,
    Links,
    Node_position,
    App_config,
    Map_name
)
from database import db
from collections import Counter, OrderedDict
import pandas as pd
from .get_demand_netflow import *
import json
from influxdb import InfluxDBClient
from sqlalchemy import or_, and_
from .snmp_influx import get_max_util
from .mutils import *
import collections
from functools import reduce

blueprint = Blueprint(
    "data_blueprint",
    __name__,
    url_prefix="/data",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/topology")
@login_required
def topology():
    current_user = str(session["_user_id"])
    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    df = pd.read_sql(
        db.session.query(Links).filter(Links.index >= 0).statement, db.session.bind
    )
    isis_links = df.to_dict(orient="records")
    map_name = Map_name.query.all()
    return render_template(
        "topology.html", values=isis_links, node_position=node_position,map_name=map_name
    )


@blueprint.route("/topology_region1")
@login_required
def topology_region1():
    current_user = str(session["_user_id"])
    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    df = pd.read_sql(
        db.session.query(Links).filter(Links.index >= 0).statement, db.session.bind
    )
    isis_links = df.to_dict(orient="records")
    return render_template(
        "topology_region1.html", values=isis_links, node_position=node_position
    )


@blueprint.route("/topology_nested")
@login_required
def topology_nested():
    current_user = session["_user_id"]
    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    try:
        df = pd.read_sql(
            db.session.query(Links).filter(Links.index >= 0).statement, db.session.bind
        )
        df["node"] = df["source"]
        df["source"] = df.apply(lambda row: row["source"][:2], axis=1)
        df["target"] = df.apply(lambda row: row["target"][:2], axis=1)
        df = df[df["source"] != df["target"]]
        isis_links = df.to_dict(orient="records")
    except Exception as e:
        isis_links = []
    # print isis_links
    return render_template(
        "topology_nested.html", values=isis_links, node_position=node_position
    )


@blueprint.route("/topology_nested_aggregated")
@login_required
def topology_nested_aggregated():
    current_user = session["_user_id"]
    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    try:
        df = pd.read_sql(
            db.session.query(Links).filter(Links.index >= 0).statement, db.session.bind
        )
        df = df[df["source"] != df["target"]]
        df["source"] = df.apply(lambda row: row["source"][:2], axis=1)
        df["target"] = df.apply(lambda row: row["target"][:2], axis=1)
        df_aggregate = (
            df.groupby(["source", "target"])
            .agg({"util": "sum", "capacity": "sum"})
            .reset_index()
        )
        df_aggregate.loc[:, "l_ip_r_ip"] = pd.Series(
            [
                tuple(sorted(each))
                for each in list(
                    zip(
                        df_aggregate.source.values.tolist(),
                        df_aggregate.target.values.tolist(),
                    )
                )
            ]
        )
        isis_links = df_aggregate.to_dict(orient="records")
    except Exception as e:
        isis_links = []
    # print isis_links
    return render_template(
        "topology_nested_aggregated.html",
        values=isis_links,
        node_position=node_position,
    )



@blueprint.route("/filter_topology", methods=["GET", "POST"])
@login_required
def filter_topology():
    current_user = session["_user_id"]
    node_position = pd.read_sql(
        db.session.query(Node_position)
        .filter(Node_position.user == current_user)
        .statement,
        db.session.bind,
    )
    node_position = node_position.to_dict(orient="records")
    source_filter = request.form.get("source_filter")
    target_filter = request.form.get("source_filter")
    df = pd.read_sql(
        db.session.query(Links).filter(Links.index >= 0).statement, db.session.bind
    )
    isis_links = df.to_dict(orient="records")
    return render_template(
        "filter_topology.html",
        values=isis_links,
        source_filter=source_filter,
        target_filter=target_filter,
        node_position=node_position,
    )





