"""Post requests."""
import pathlib
import uuid
import os
import flask
from flask import request, abort
import insta485


@insta485.app.route('/comments/', methods=['POST'])
def edit_comments():
    """Edit comments."""
    connection = insta485.model.get_db()
    url = request.args.get('target')
    if url is None:
        url = '/'
    logname = flask.session['username']
    operation = request.form.get('operation')
    postid = request.form.get('postid')
    commentid = request.form.get('commentid')
    text = request.form.get('text')
    if operation == 'create':
        if text == '':
            abort(400)
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (? , ?, ?)", (logname, postid, text)
        )
    if operation == 'delete':
        owners = (connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE comments.commentid=:id ",
            {"id": commentid}
        )).fetchall()
        if owners[0]['owner'] != logname:
            abort(403)
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid=:id", {"id": commentid}
        )
    return flask.redirect(url)


@insta485.app.route('/likes/', methods=['POST'])
def edit_likes():
    """Edit likes."""
    connection = insta485.model.get_db()
    url = request.args.get('target')
    if url is None:
        url = '/'
    logname = flask.session['username']
    operation = request.form.get('operation')
    postid = request.form.get('postid')
    likes = (connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE likes.postid=:postid ",
        {"postid": postid}
    )).fetchall()
    usernames = []
    for like in likes:
        usernames.append(like['owner'])
    if operation == 'like':
        if logname in usernames:
            abort(409)
        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (? , ?)", (logname, postid)
        )
    if operation == 'unlike':
        if logname not in usernames:
            abort(409)
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner=:logname AND postid=:postid",
            {"logname": logname, "postid": postid}
        )
    return flask.redirect(url)


@insta485.app.route('/following/', methods=['POST'])
def edit_following():
    """Edit following."""
    connection = insta485.model.get_db()
    url = request.args.get('target')
    if url is None:
        url = '/'
    logname = flask.session['username']
    operation = request.form.get('operation')
    username = request.form.get('username')
    following = (connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE following.username1=:logname ",
        {"logname": logname}
    )).fetchall()
    usernames = []
    for follow in following:
        usernames.append(follow['username2'])
    if operation == 'follow':
        if username in usernames:
            abort(409)
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (? , ?)", (logname, username)
        )
    if operation == 'unfollow':
        if username not in usernames:
            abort(409)
        connection.execute(
            "DELETE FROM following "
            "WHERE username1=:logname AND username2=:username",
            {"logname": logname, "username": username}
        )
    return flask.redirect(url)


@insta485.app.route('/posts/', methods=['POST'])
def edit_posts():
    """Edit posts."""
    connection = insta485.model.get_db()
    logname = flask.session['username']
    url = request.args.get('target')
    if url is None:
        url = '/users/' + logname + '/'
    operation = request.form.get('operation')
    postid = request.form.get('postid')
    if operation == 'create':
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        uuid_basename = f"{uuid.uuid4().hex}{pathlib.Path(filename).suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        if os.stat(path).st_size == 0:
            abort(400)
        connection.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (? , ?)", (uuid_basename, logname)
        )
    if operation == 'delete':
        post_owners = (connection.execute(
            "SELECT owner, "
            "filename "
            "FROM posts "
            "WHERE posts.postid=:postid ",
            {"postid": postid}
        )).fetchall()
        post_owner = []
        for owner in post_owners:
            post_owner.append(owner["owner"])
        if logname not in post_owner:
            abort(403)
        for filename in post_owners:
            # print(filename)
            file = filename["filename"]
        # rem = insta485.app.config["UPLOAD_FOLDER"]/file
        os.remove(insta485.app.config["UPLOAD_FOLDER"]/file)
        p_id = int(postid)
        connection.execute(
            "DELETE FROM posts "
            "WHERE postid=:id",
            {"id": p_id}
        )
    return flask.redirect(url)
