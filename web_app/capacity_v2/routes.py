

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
import json
from influxdb import InfluxDBClient
from sqlalchemy import or_, and_
from .mutils import *
import collections
from functools import reduce

blueprint = Blueprint(
    "capacity_blueprint",
    __name__,
    url_prefix="/capacity",
    template_folder="templates",
    static_folder="static",
)

@blueprint.route('/interface_graph')
@login_required
def interface_graph():
    routers = Routers.query.all()
    router_name = [ router.name for router in routers ]
    interface_name = ''
    return render_template('interface_graph.html',router_name=router_name,interface_name=interface_name)

@blueprint.route("/traffic_links", methods=["GET", "POST"])
@login_required
def traffic_links():
    INFLUXDB_HOST = "127.0.0.1"
    INFLUXDB_NAME = "telegraf"
    client = InfluxDBClient(INFLUXDB_HOST, "8086", "", "", INFLUXDB_NAME)
    source_filter = request.form.get("source_cc")
    target_filter = request.form.get("target_cc")
    interval = request.form.get("time_cc")
    max_value = 0
    df_csv = ""
    df_year = ""
    if (source_filter == None) or (target_filter == None) or (interval == None):
        source_filter = "gb%"
        target_filter = "fr%"
        # interval = 480
        interval = 24
    else:
        source_filter = source_filter + "%"
        target_filter = target_filter + "%"

    qry = (
        db.session.query(Links)
        .filter(
            and_(Links.source.like(source_filter), Links.target.like(target_filter))
        )
        .statement
    )
    df = pd.read_sql(qry, db.session.bind)
    if not df.empty:
        df["max_util"] = df.apply(
            lambda row: get_max_util(row["source"], row["l_int"], interval), axis=1
        )
        isis_links = df.to_dict(orient="records")
        total_capacity = df["capacity"].sum()
    else:
        isis_links = []
    df_countries = pd.read_sql(
        db.session.query(Routers.country.distinct()).statement, db.session.bind
    )
    countries = df_countries.to_dict(orient="records")
    # get the last 24h for each link between the countries
    df_variable = []
    if len(isis_links) == 0:
        max_value = 0
        total_capacity = 0
        df_csv = 0
        df_year = 0
    else:
        try:

        # create a dict for each link
            df_dict = df.to_dict(orient="records")
            for i in df_dict:
                queryurl = """SELECT non_negative_derivative(mean(ifHCOutOctets), 1s) *8 from interface_statistics
                            where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh
                            group by time(5m)""" % (
                i["source"],
                i["l_int"],
                interval,
                )
                result = client.query(queryurl)
                points = list(result.get_points(measurement="interface_statistics"))
                df_max = pd.DataFrame(points)
                if not df_max.empty:
                    df_variable.append(df_max)
        # print df_variable
        # merge the values
            df_merged = reduce(
                lambda left, right: pd.merge(left, right, on=["time"], how="outer"),
                df_variable,
            ).fillna(0)
        # print df_merged
        # get the sum
            df_merged["bps"] = df_merged.drop("time", axis=1).sum(axis=1)
            df_merged = df_merged.sort_values(by=["time"])
        # with the sum pass this to graph
            df_csv = df_merged.to_dict(orient="records")
        # df_csv=df_merged.reindex(columns=["time","bps"]).to_csv(index=False)
            max_value = df_merged["bps"].max()
            max_value = max_value / 1000000
            df_year = generate_year_graph(source_filter[:-1], target_filter[:-1])
            df_year = df_year.to_dict(orient="records")
        except:
            pass
    return render_template(
        "traffic_links.html",
        values=isis_links,
        countries=countries,
        max_value=int(max_value),
        graph=df_csv,
        total_capacity=total_capacity,
        s_c=source_filter[:-1],
        t_c=target_filter[:-1],
        df_year=df_year,
    )
