"""
Insta485 explore view.

URLs include:
/
"""
import flask
from flask import url_for
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'username' in flask.session:
        # Sets up the context dictionary
        context = {}
        logname_explore = flask.session['username']
        context['logname'] = logname_explore
        # Connect to database
        connection = insta485.model.get_db()
        # Gets all of following information
        following_explore = (connection.execute(
            "SELECT "
            "username1, "
            "username2 "
            "FROM following "
            "WHERE username1=:logname",
            {"logname": logname_explore}
        )).fetchall()
        follows = []
        follows.append(logname_explore)
        for item in following_explore:
            follows.append(item['username2'])
        # Gets all of the user information
        # # account picture
        # account_picture = (connection.execute(
        #     "SELECT "
        #     "filename "
        #     "FROM users "
        #     "WHERE username=:user",
        #     {"user": logname_explore}
        # )).fetchall()
        # for item in account_picture:
        #     context['account_picture'] = url_for(
        #         'download_file',filename=item['filename'])
        users_explore = (connection.execute(
            "SELECT DISTINCT "
            "username, "
            "filename AS user_img_url "
            "FROM users "
        )).fetchall()
        # finds users that logged in user is not following
        context['not_following'] = []
        for user in users_explore:
            user['user_img_url'] = url_for('download_file',
                                           filename=user['user_img_url'])
            if user['username'] not in follows:
                context['not_following'].append(user)
        return flask.render_template("explore.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
