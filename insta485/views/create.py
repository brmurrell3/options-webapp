"""
Insta485 login view.

URLs include:
/accounts/create/
"""

import flask
import insta485


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create_prelim():
    """Display /accounts/login/ route."""
    flask.session.clear()
    if 'username' in flask.session:
        # not sure if this works because it is never triggered
        return flask.redirect(flask.url_for('create_edit'))
    return flask.render_template('/accounts/create.html')
