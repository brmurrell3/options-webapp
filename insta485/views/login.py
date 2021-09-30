"""
Insta485 login view.

URLs include:
/accounts/login/
"""

import flask
import insta485


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def check_login_status():
    """Display /accounts/login/ route."""
    if 'username' in flask.session:
        # not sure if this works because it is never triggered
        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template('/accounts/login.html')
