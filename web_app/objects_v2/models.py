from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

from database import Base

from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode


tags = Table(
    "tags",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("Tag.id")),
    Column("router_name", Integer, ForeignKey("Routers.name")),
)











class Node_position_global(Base):
    __tablename__ = "Node_position_global"

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)
    map_type = Column(String(120), primary_key=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)


class Tag(Base):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Routers(Base, UserMixin):

    __tablename__ = "Routers"

    tags = relationship(
        "Tag", secondary=tags, backref=backref("Routers", lazy="dynamic")
    )

    index = Column(Integer, autoincrement=True)
    name = Column(String(300), primary_key=True, unique=True)
    ip = Column(String(120), unique=True)
    country = Column(String(30))
    vendor = Column(String(30))
    model = Column(String(250))
    version = Column(String(250))
    tacacs_id = Column(String(250), ForeignKey("Tacacs.id"), default="0")
    tacacs = relationship("Tacacs", backref="parents")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Prefixes(Base, UserMixin):

    __tablename__ = "Prefixes"

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
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class Links(Base, UserMixin):

    __tablename__ = "Links"

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
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)




class Node_position(Base, UserMixin):

    __tablename__ = "Node_position"

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)


class Node_position_temp(Base, UserMixin):

    __tablename__ = "Node_position_temp"

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)




class rpc_routers(Base, UserMixin):

    __tablename__ = "rpc_routers"

    index = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class rpc_prefixes(Base, UserMixin):

    __tablename__ = "rpc_prefixes"

    index = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    ip = Column(String(120), unique=True)
    country = Column(String(30))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)


class rpc_links(Base, UserMixin):

    __tablename__ = "rpc_links"

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
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.l_ip)



class External_topology_temp(Base, UserMixin):

    __tablename__ = "External_topology_temp"

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
    alert_status = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class External_topology(Base, UserMixin):

    __tablename__ = "External_topology"

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
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.index)


class External_position(Base, UserMixin):

    __tablename__ = "External_position"

    id = Column(String(120), primary_key=True)
    user = Column(String(120), primary_key=True)
    x = Column(String(120), unique=False)
    y = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)



class Script_run(Base):

    __tablename__ = "Script_run"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)





class App_config(Base):

    __tablename__ = "App_config"

    asn = Column(String(300), primary_key=True)
    web_ip = Column(String(120), unique=True)
    influx_ip = Column(String(120), unique=True)
    nb_url = Column(String(120), unique=True)
    nb_token = Column(String(120), unique=True)
    master_key = Column(String(120), unique=True)
    alert_threshold = Column(String(120), unique=False)
    alert_backoff = Column(String(120), unique=False)
    menu_style = Column(String(120), unique=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.asn)



class Tacacs(Base):
    """Tacacs table , links with Routers"""

    __tablename__ = "Tacacs"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), unique=True)
    username = Column(String(300), unique=False)
    password = Column(String(300), unique=False)

    def __init__(self, master_key=None, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            if property == "password":
                cipher = encrypt(master_key, value)
                encoded_cipher = b64encode(cipher)
                setattr(self, property, encoded_cipher)
            else:
                setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

class Map_name(Base, UserMixin):
    __tablename__ = "Map_name"

    name = Column(String(300), unique=True,primary_key=True)
    regexp = Column(String(120), unique=False)
    regexptar = Column(String(120), unique=False)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

class Support(Base, UserMixin):
    __tablename__ = "Support"

    name = Column(String(300), unique=True,primary_key=True)
    email = Column(String(120), unique=False)
    message = Column(String(120), unique=False)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                (value,) = value
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)
