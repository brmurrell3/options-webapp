"""
Insta485 followers view.

URLs include:

"""
import flask
from flask import url_for, abort
import insta485


@insta485.app.route('/users/<path:user>/followers/')
def show_followers(user):
    """Display /explore/ route."""
    if 'username' in flask.session:
        context = {}
        logname_followers = flask.session['username']
        context['logname'] = logname_followers
        context['user'] = user
        # Connect to database
        connection = insta485.model.get_db()
        # Error checking
        err_followers = (connection.execute(
            "SELECT "
            "username "
            "FROM users "
            "WHERE username=:user_fo",
            {"user_fo": user}
        )).fetchall()
        if len(err_followers) == 0:
            abort(404)
        # Gets all people who follow logged in user
        followers = (connection.execute(
            "SELECT "
            "following.username1 AS username, "
            "users.filename AS user_img_url "
            "FROM following "
            "LEFT JOIN users ON following.username1 = users.username "
            "WHERE username2=:user",
            {"user": user}
        )).fetchall()
        # Gets all people who user follows
#        cur2 = connection.execute(
#            "SELECT "
#            "username2 AS username "
#            "FROM following "
#            "WHERE username1=:user",
#            {"user": user}
#        )
#        following = cur2.fetchall()
        # Gets all people logname follows
        following_logname = (connection.execute(
            "SELECT "
            "username2 AS username "
            "FROM following "
            "WHERE username1=:logged",
            {"logged": logname_followers}
        )).fetchall()
        following_list = []
        for follow in following_logname:
            following_list.append(follow['username'])
        context['followers'] = []
        for follower in followers:
            temp = follower['user_img_url']
            follower['user_img_url'] = url_for('download_file', filename=temp)
            if follower['username'] in following_list:
                follower['logname_follows_username'] = True
            else:
                follower['logname_follows_username'] = False
            context['followers'].append(follower)
        return flask.render_template("followers.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
