"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import url_for
from flask import send_from_directory
import arrow
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # flask.session['username'] = 'awdeorio'
    if 'username' in flask.session:
        context = {}
        logname_index = flask.session['username']
        context['logname'] = logname_index
        # Connect to database
        connection = insta485.model.get_db()
        # Gets all of the post information
        posts = (connection.execute(
            "SELECT DISTINCT posts.postid AS postid, "
            "posts.owner AS owner, "
            "users.filename AS owner_img_url, "
            "posts.filename AS img_url, "
            "posts.created AS timestamp, "
            "COUNT(likes.postid) AS likes "
            "FROM posts "
            "LEFT JOIN users "
            "ON posts.owner = users.username "
            "LEFT JOIN likes ON likes.postid = posts.postid "
            "GROUP BY posts.postid "
            "ORDER BY posts.postid DESC"
        )).fetchall()
        # Gets all of the comment information
        comments = (connection.execute(
            "SELECT "
            "* "
            "FROM comments "
            "ORDER BY commentid "
        )).fetchall()
        # Gets all of the like information
        likes = (connection.execute(
            "SELECT "
            "* "
            "FROM likes "
        )).fetchall()
        # Gets all of the following information
        following = (connection.execute(
            "SELECT "
            "username2 "
            "FROM following "
            "WHERE username1=:logged_in",
            {"logged_in": logname_index}
        )).fetchall()
        # account picture
        account_picture = (connection.execute(
            "SELECT "
            "filename "
            "FROM users "
            "WHERE username=:user",
            {"user": logname_index}
        )).fetchall()
        for item in account_picture:
            context['account_picture'] = url_for(
                'download_file', filename=item['filename'])
        like_dict = {}
        for post in posts:
            like_dict[post['postid']] = []
        for like in likes:
            like_dict[like['postid']].append(like['owner'])
        follow_lst = []
        for follow in following:
            follow_lst.append(follow['username2'])
        follow_lst.append(logname_index)
        # Add database info to context
        context['posts'] = []
        for post in posts:
            if post['owner'] in follow_lst:
                # making the pictures work
                combine(post, comments, logname_index, like_dict, context)
        return flask.render_template("index.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))


def combine(post, comments, logname_index, like_dict, context):
    """Send from directory."""
    # making the pictures work
    post['owner_img_url'] = url_for('download_file',
                                    filename=post['owner_img_url'])
    post['img_url'] = url_for('download_file',
                              filename=post['img_url'])
    # humanizing time
    arrow.get(post['timestamp'])
    post['timestamp'] = (
        (arrow.utcnow()).to('US/Eastern')).humanize()
    # adding comments to the post
    comment_temp = []
    for comment in comments:
        if comment['postid'] == post['postid']:
            comment_temp.append(comment)
    post['comments'] = comment_temp
    # figuring out like/unlike button
    if logname_index in like_dict[post['postid']]:
        post['button'] = 0
    else:
        post['button'] = 1
    # checking to make sure that post will be shown
    context['posts'].append(post)


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Send from directory."""
    if 'username' not in flask.session:
        flask.abort(403)
    if not (insta485.app.config['UPLOAD_FOLDER']/filename).is_file():
        flask.abort(404)
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)
