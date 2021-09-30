"""
Insta485 following view.

URLs include:

"""
import flask
from flask import url_for, abort
import insta485


@insta485.app.route('/users/<path:user>/following/')
def show_following(user):
    """Display /explore/ route."""
    if 'username' in flask.session:
        context = {}
        logname_following = flask.session['username']
        context['logname'] = logname_following
        context['user'] = user
        # Connect to database
        connection = insta485.model.get_db()
        # Checks for errors
        err_following = (connection.execute(
            "SELECT "
            "username "
            "FROM users "
            "WHERE username=:err",
            {"err": user}
        )).fetchall()
        if len(err_following) == 0:
            abort(404)
        # Gets all people the logged in user is following
        following = (connection.execute(
            "SELECT "
            "following.username2 AS username, "
            "users.filename AS user_img_url "
            "FROM following "
            "LEFT JOIN users ON following.username2 = users.username "
            "WHERE username1=:user",
            {"user": user}
        )).fetchall()
        # Gets all people who user follows
#        cur2 = connection.execute(
#            "SELECT "
#            "following.username2 AS username "
#            "FROM following "
#            "WHERE username1=:user",
#            {"user": user}
#        )
#        following2 = cur2.fetchall()
        # Gets all people logname follows
        following_logged_in = (connection.execute(
            "SELECT "
            "username2 AS username "
            "FROM following "
            "WHERE username1=:logname",
            {"logname": logname_following}
        )).fetchall()
        following_list = []
        for follow in following_logged_in:
            following_list.append(follow['username'])
        context['following'] = []
        for follow in following:
            follow['user_img_url'] = url_for('download_file',
                                             filename=follow['user_img_url'])
            if follow['username'] in following_list:
                follow['logname_follows_username'] = True
            else:
                follow['logname_follows_username'] = False
            context['following'].append(follow)
        return flask.render_template("following.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
