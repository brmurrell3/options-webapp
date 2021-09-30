"""
Insta485 post (password) view.

URLs include:
/
"""

import flask
import insta485


@insta485.app.route('/accounts/password/')
def show_pass():
    """Display password route."""
    if 'username' in flask.session:
        # Sets logname
        context = {}
        logname_password = flask.session['username']
        context['logname'] = logname_password
        return flask.render_template("accounts/password.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
