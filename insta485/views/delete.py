"""
Insta485 login view.

URLs include:
/accounts/create/
"""

import flask
import insta485


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def delete_prelim():
    """Display /accounts/edit/ route."""
    if 'username' in flask.session:
        context = {}
        logname_delete = flask.session['username']
        context['logname'] = logname_delete
        return flask.render_template('/accounts/delete.html', **context)
    return flask.redirect(flask.url_for('check_login_status'))
