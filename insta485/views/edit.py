"""
Insta485 login view.

URLs include:
/accounts/edit/
"""

import flask
import insta485


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def create_edit():
    """Display /accounts/edit/ route."""
    if 'username' in flask.session:
        context = {}
        logname_edit = flask.session['username']
        context['logname'] = logname_edit
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT email, fullname, filename "
            "FROM users "
            "WHERE username=:logname_edit ",
            {"logname_edit": logname_edit}
        )

        data = cur.fetchall()

        context['email'] = data[0]['email']
        context['fullname'] = data[0]['fullname']
        temp_filename = data[0]['filename']
        context['filename'] = flask.url_for('download_file',
                                            filename=temp_filename)

        return flask.render_template("/accounts/edit.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
