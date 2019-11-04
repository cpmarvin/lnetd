from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,backref

from database import Base

from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode


tags = Table('tags',Base.metadata,
                Column('tag_id', Integer, ForeignKey('Tag.id')),
                Column('router_name', Integer, ForeignKey('Routers.name')),
                )

class Node_position_global(Base):
    __tablename__ = 'Node_position_global'

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)
    map_type = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)

class Tag(Base):
    __tablename__ = 'Tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

class Routers(Base, UserMixin):

    __tablename__ = 'Routers'

    tags = relationship('Tag', secondary=tags,
                           backref=backref('Routers', lazy='dynamic'))

    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    ip = Column(String(120), unique=True)
    country = Column(String(30))
    vendor = Column(String(30))
    model = Column(String(30))
    version = Column(String(250))
    tacacs_id = Column(String(250), ForeignKey("Tacacs.id"), default="0")
    tacacs = relationship("Tacacs", backref="parents")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Prefixes(Base, UserMixin):

    __tablename__ = 'Prefixes'

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    ip = Column(String(120), unique=True)
    country = Column(String(30))
    version = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Links(Base, UserMixin):

    __tablename__ = 'Links'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=True)
    metric = Column(String(120), unique=False)
    l_int = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=True)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    errors = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class Links_time(Base, UserMixin):

    __tablename__ = 'Links_time'

    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(Integer, unique=False)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=False)
    metric = Column(String(120), unique=False)
    l_int = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=False)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    errors = Column(String(120), unique=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class Links_latency(Base, UserMixin):

    __tablename__ = 'Links_latency'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=True)
    metric = Column(String(120), unique=False)
    l_int = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=True)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    errors = Column(String(120), unique=False)
    latency = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class Node_position(Base, UserMixin):

    __tablename__ = 'Node_position'

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)


class Node_position_temp(Base, UserMixin):

    __tablename__ = 'Node_position_temp'

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)


class isisd_routers(Base, UserMixin):

    __tablename__ = 'isisd_routers'

    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class isisd_prefixes(Base, UserMixin):

    __tablename__ = 'isisd_prefixes'

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class isisd_links(Base, UserMixin):

    __tablename__ = 'isisd_links'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=True)
    metric = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=True)
    l_ip_r_ip = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class rpc_routers(Base, UserMixin):

    __tablename__ = 'rpc_routers'

    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class rpc_prefixes(Base, UserMixin):

    __tablename__ = 'rpc_prefixes'

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class rpc_links(Base, UserMixin):

    __tablename__ = 'rpc_links'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=True)
    metric = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=True)
    l_ip_r_ip = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class External_topology_temp(Base, UserMixin):

    __tablename__ = 'External_topology_temp'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    node = Column(String(120), unique=False)
    interface = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    direction = Column(String(120), unique=False)
    src_icon = Column(String(120), unique=False)
    tar_icon = Column(String(120), unique=False)
    cir = Column(String(120), unique=False)
    type = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class External_topology(Base, UserMixin):

    __tablename__ = 'External_topology'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    node = Column(String(120), unique=False)
    interface = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    direction = Column(String(120), unique=False)
    src_icon = Column(String(120), unique=False)
    tar_icon = Column(String(120), unique=False)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    cir = Column(String(120), unique=False)
    type = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class External_position(Base, UserMixin):

    __tablename__ = 'External_position'

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)


class International_PoP_temp(Base, UserMixin):

    __tablename__ = 'International_PoP_temp'

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    routers = Column(String(120), unique=False)
    region = Column(String(120), unique=False)
    lat = Column(String(120), unique=False)
    lon = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class International_PoP(Base, UserMixin):

    __tablename__ = 'International_PoP'

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    routers = Column(String(120), unique=False)
    region = Column(String(120), unique=False)
    lat = Column(String(120), unique=False)
    lon = Column(String(120), unique=False)
    util_out = Column(String(120), unique=False)
    util_in = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    text = Column(String(420), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class Inventory_cards(Base, UserMixin):

    __tablename__ = 'Inventory_cards'
    index = Column(Integer, primary_key=True)
    card_name = Column(String(120))
    card_slot = Column(String(120))
    card_status = Column(String(120))
    router_name = Column(String(120))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.router_name)


class Inventory_interfaces(Base, UserMixin):

    __tablename__ = 'Inventory_interfaces'
    index = Column(Integer, primary_key=True)
    interface_name = Column(String(120))
    interface_status = Column(String(120))
    interface_speed = Column(String(120))
    router_name = Column(String(120), primary_key=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.router_name)


class Script_run(Base):

    __tablename__ = 'Script_run'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Bgp_peers(Base):

    __tablename__ = 'Bgp_peers'

    index = Column(Integer, primary_key=True)
    router = Column(String(120), unique=False)
    neighbour = Column(String(120), unique=False)
    neighbour_ip = Column(String(120), unique=False)
    remote_as = Column(String(120), unique=False)
    is_up = Column(String(120), unique=False)
    type = Column(String(120), unique=False)
    accepted_prefixes = Column(String(120), unique=False)
    ix_name = Column(String(120), unique=False)
    uptime = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class Bgp_customers(Base):

    __tablename__ = 'Bgp_customers'

    index = Column(Integer, primary_key=True)
    prefix = Column(String(300), unique=True)
    asn = Column(String(120), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Bgp_peering_points(Base):

    __tablename__ = 'Bgp_peering_points'

    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    ipv4 = Column(String(120), unique=True)
    ipv6 = Column(String(120), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class App_config(Base):

    __tablename__ = 'App_config'

    asn = Column(String(300), primary_key=True)
    web_ip = Column(String(120), unique=True)
    influx_ip = Column(String(120), unique=True)
    nb_url = Column(String(120), unique=True)
    nb_token = Column(String(120), unique=True)
    master_key = Column(String(120), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.asn)


class App_external_flows(Base):
    __tablename__ = 'App_external_flows'
    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    router = Column(String(120), unique=False)
    if_index = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

# model_save_load


class Links_Model(Base, UserMixin):

    __tablename__ = 'Links_Model'

    index = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=False)
    metric = Column(String(120), unique=False)
    l_int = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=False)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    user_id = Column(String(120), unique=False)
    model_name = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class Fabric_links(Base, UserMixin):

    __tablename__ = 'Fabric_links'

    index = Column(Integer, primary_key=True)
    source = Column(String(120), unique=False)
    target = Column(String(120), unique=False)
    l_ip = Column(String(120), unique=False)
    l_int = Column(String(120), unique=False)
    r_ip = Column(String(120), unique=False)
    metric = Column(String(120), unique=False)
    l_ip_r_ip = Column(String(120), unique=False)
    util = Column(String(120), unique=False)
    capacity = Column(String(120), unique=False)
    errors = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)


class Tacacs(Base):
    __tablename__ = 'Tacacs'

    id = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    username = Column(String(300), unique=False)
    password = Column(String(300), unique=False)

    def __init__(self, master_key=None, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            if property == 'password':
                cipher = encrypt(master_key, value)
                encoded_cipher = b64encode(cipher)
                setattr(self, property, encoded_cipher)
            else:
                setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class bgp_groups(Base, UserMixin):

    __tablename__ = 'bgp_groups'

    index = Column(Integer, primary_key=True)
    group = Column(String(300), unique=False)
    router = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.router)
