"""
Insta485 logout view.

URLs include:
/accounts/logout/
"""

import flask
import insta485


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Clear session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('check_login_status'))
