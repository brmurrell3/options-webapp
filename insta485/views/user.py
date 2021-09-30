"""
Insta485 user view.

URLs include:

"""
import flask
from flask import url_for, abort
import insta485


@insta485.app.route('/users/<path:user>/')
def show_user(user):
    """Display route."""
    if 'username' in flask.session:
        context = {}
        logname_user = flask.session['username']
        context['logname'] = logname_user
        context['username'] = user
        # Connect to database
        connection = insta485.model.get_db()
        # error checking
        err_user = (connection.execute(
            "SELECT "
            "username "
            "FROM users "
            "WHERE username=:user",
            {"user": user}
        )).fetchall()
        if len(err_user) == 0:
            abort(404)
        # Gets all of following information
        following = (connection.execute(
            "SELECT "
            "username2 "
            "FROM following "
            "WHERE username1=:logname",
            {"logname": logname_user}
        )).fetchall()
        follows = []
        for item in following:
            follows.append(item['username2'])
        follows.append(logname_user)
        # Relationship
        if user in follows:
            context['logname_follows_username'] = True
        else:
            context['logname_follows_username'] = False
        # full name
        full_name = (connection.execute(
            "SELECT DISTINCT "
            "fullname "
            "FROM users "
            "WHERE username=:user",
            {"user": user}
        )).fetchall()
        for item in full_name:
            context['fullname'] = item['fullname']
        # profile picture
        profile_picture = (connection.execute(
            "SELECT "
            "filename "
            "FROM users "
            "WHERE username=:user",
            {"user": user}
        )).fetchall()
        for item in profile_picture:
            context['profile_picture'] = url_for(
                'download_file', filename=item['filename'])
        # account picture
        zccount_picture = (connection.execute(
            "SELECT "
            "filename "
            "FROM users "
            "WHERE username=:user",
            {"user": logname_user}
        )).fetchall()
        for item in zccount_picture:
            context['account_picture'] = url_for(
                'download_file', filename=item['filename'])
        # following
        following2 = (connection.execute(
            "SELECT DISTINCT "
            "username2 "
            "FROM following "
            "WHERE username1=:user",
            {"user": user}
        )).fetchall()
        # followers
        followers = (connection.execute(
            "SELECT DISTINCT "
            "username1 "
            "FROM following "
            "WHERE username2=:user",
            {"user": user}
        )).fetchall()
        context['following'] = len(following2)
        context['followers'] = len(followers)
        posts = (connection.execute(
            "SELECT "
            "postid, "
            "filename AS img_url "
            "FROM posts "
            "WHERE owner=:user",
            {"user": user}
        )).fetchall()
        context['total_posts'] = len(posts)
        context['posts'] = []
        for post in posts:
            post['img_url'] = url_for('download_file',
                                      filename=post['img_url'])
            print(post['img_url'])
            context['posts'].append(post)
        return flask.render_template("user.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
