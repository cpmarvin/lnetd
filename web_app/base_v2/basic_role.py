# simple role based
from functools import wraps
from flask_login import current_user
from flask import url_for, redirect


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.get_current_user_role() not in roles:
                return redirect(url_for('base_blueprint.no_admin'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# end simple role based
