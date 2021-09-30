"""
Insta485 post (main) view.

URLs include:
/
"""
import flask
from flask import url_for
import arrow
import insta485


@insta485.app.route('/posts/<path:p_id>/')
def show_post(p_id):
    """Display / route."""
    if 'username' in flask.session:
        # Sets logname
        context = {}
        logname_post = flask.session['username']
        context['logname'] = logname_post
        context['postid'] = p_id
        # Connect to database
        connection = insta485.model.get_db()
        # Gets all of the post information
        posts = (connection.execute(
            "SELECT DISTINCT "
            "posts.owner AS owner, "
            "posts.filename AS img_url, "
            "users.filename AS owner_img_url, "
            "posts.created AS timestamp, "
            "COUNT(likes.postid) AS likes "
            "FROM posts "
            "LEFT JOIN users ON posts.owner = users.username "
            "LEFT JOIN likes ON likes.postid = posts.postid "
            "WHERE posts.postid=:id ",
            {"id": p_id}
        )).fetchall()
        # Gets all the likes
        likes_post = (connection.execute(
            "SELECT "
            "owner "
            "FROM likes "
            "WHERE postid=:id ", {"id": p_id}
        )).fetchall()
        # Gets all of the comment information
        comments_post = (connection.execute(
            "SELECT "
            "* "
            "FROM comments "
            "ORDER BY commentid "
        )).fetchall()
        like_lst = []
        for like in likes_post:
            like_lst.append(like['owner'])
        # Add database info to context
        for post in posts:
            context['owner'] = post['owner']
            context['owner_img_url'] = url_for('download_file',
                                               filename=post['owner_img_url'])
            context['img_url'] = url_for('download_file',
                                         filename=post['img_url'])
            context['likes'] = post['likes']
            # humanizing time
            arrow.get(post['timestamp'])
            local = ((arrow.utcnow()).to('US/Eastern'))
            context['timestamp'] = local.humanize()
            # adding comments to the post
            comment_temp = []
            for comment in comments_post:
                if comment['postid'] == int(p_id):
                    comment_temp.append(comment)
            context['comments'] = comment_temp
            # figuring out like/unlike button
            if logname_post in like_lst:
                context['button'] = 0
            else:
                context['button'] = 1
        return flask.render_template("post.html", **context)
    return flask.redirect(flask.url_for('check_login_status'))
