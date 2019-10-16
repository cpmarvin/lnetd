from flask import Blueprint, render_template, request
from flask_login import login_required
import pandas as pd
from database import db
from sqlalchemy import or_, and_, func

blueprint = Blueprint(
    'inventory_blueprint',
    __name__,
    url_prefix='/inventory',
    template_folder='templates',
    static_folder='static'
)


from database import db
from objects.models import Routers, Inventory_cards, Inventory_interfaces


@blueprint.route('/inventory_cards')
@login_required
def inventory_cards():
    cards = Inventory_cards.query.all()
    return render_template('inventory_cards.html', values=cards)


@blueprint.route('/inventory_interface')
@login_required
def inventory_interface():
    interface = Inventory_interfaces.query.all()
    return render_template('inventory_interface.html', values=interface)


@blueprint.route('/inventory_device', methods=['GET', 'POST'])
@login_required
def inventory_device():
    device_cc = request.form.get('device_cc')
    # get list of routers from inventory
    df_router_name = pd.read_sql(db.session.query(
        Inventory_cards.router_name.distinct()).statement, db.session.bind)
    router_name = df_router_name.sort_values(
        by='anon_1').to_dict(orient='records')
    if (device_cc == None):
        #device_cc = 'gb-pe8-lo'
        return render_template('inventory_device.html', router_name=router_name, device_cc='',
                           cards='', values='',
                           router_model='', router_model_js='',
                           rtr_interfaces='',
                           cards_inv='')
    # get router model
    qry = db.session.query(Routers).filter(
        and_(Routers.name.like(device_cc))).statement
    df = pd.read_sql(qry, db.session.bind)
    router_model = str(df['model'][0])
    router_model_js = router_model.replace("-", "_")
    # get all interface from device
    qry = db.session.query(Inventory_interfaces).filter(
        and_(Inventory_interfaces.router_name.like(device_cc))).statement
    df = pd.read_sql(qry, db.session.bind)
    interface = df.to_dict(orient='records')
    # get all cards from device
    qry = db.session.query(Inventory_cards).filter(
        and_(Inventory_cards.router_name.like(device_cc))).statement
    df = pd.read_sql(qry, db.session.bind)
    cards = df.to_dict(orient='records')
    cards_inv = df['card_slot'].values.tolist()
    # up interfaces
    qry = db.session.query(Inventory_interfaces.interface_speed, func.count(Inventory_interfaces.interface_status)).filter(
        and_(Inventory_interfaces.router_name.like(device_cc),
             Inventory_interfaces.interface_status.like('Up%'))).group_by(
        Inventory_interfaces.interface_speed).statement
    df_up = pd.read_sql(qry, db.session.bind)
    # down interfaces
    qry = db.session.query(Inventory_interfaces.interface_speed, func.count(Inventory_interfaces.interface_status)).filter(
        and_(Inventory_interfaces.router_name.like(device_cc),
             Inventory_interfaces.interface_status.like('Down%'))).group_by(
        Inventory_interfaces.interface_speed).statement
    df_down = pd.read_sql(qry, db.session.bind)
    # merge the two df
    df_final = df_up.merge(df_down, on='interface_speed', how='outer')
    # add correct columns
    df_final.columns = ['interface_speed', 'up', 'down']
    # add 0 instead of NA
    rtr_interfaces = df_final.fillna(0)
    rtr_interfaces = rtr_interfaces.to_dict(orient='records')
    return render_template('inventory_device.html', router_name=router_name, device_cc=device_cc,
                           cards=cards, values=interface,
                           router_model=router_model, router_model_js=router_model_js,
                           rtr_interfaces=rtr_interfaces,
                           cards_inv=cards_inv)
