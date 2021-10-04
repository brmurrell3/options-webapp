"""REST API for posts."""
import flask
import hashlib
from flask import request
import insta485


def encrypt(base_input, salt):
    """Encrypt."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + base_input
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string
    
    
def login(connection):
    """Check credentials."""
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    data = (connection.execute(
        "SELECT DISTINCT username, password "
        "FROM users WHERE username=:temp ",
        {'temp': str(username)}
    )).fetchall()
    # If username and password authentication fails, abort(403).
    if not data:  # the username search returned null
        return 'failed'
    dbpass = data[0]['password']
    dbsalt = (dbpass.split('$'))[1]
    # If username and password authentication fails, abort(403).
    if dbpass != encrypt(password, dbsalt):
        return 'failed'
    return 'succeeded'


@insta485.app.route('/api/v1/', methods=['GET'])
def get_services():
    """Return general info."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Return post on postid."""
    context = {}
    connection = insta485.model.get_db()
    if flask.request.authorization['username'] is None or login(connection) == 'failed':
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return flask.jsonify(**context), 403
    size = (connection.execute(
        "SELECT "
        "COUNT(postid) AS num "
        "FROM posts "
    )).fetchall()
    if int(size[0]['num']) < int(postid_url_slug):
        context['message'] = "Not found"
        context['status_code'] = 404
        return flask.jsonify(**context), 404
    comments = {}
    likes = {}
    post = (connection.execute(
        "SELECT DISTINCT "
        "posts.owner AS owner, "
        "posts.filename AS img_url, "
        "users.filename AS owner_img_url, "
        "posts.created AS created, "
        "COUNT(likes.postid) AS likes "
        "FROM posts "
        "LEFT JOIN users ON posts.owner = users.username "
        "LEFT JOIN likes ON likes.postid = posts.postid "
        "WHERE posts.postid=:post_id ",
        {"post_id": postid_url_slug}
    )).fetchall()
    comments = (connection.execute(
        "SELECT "
        "* "
        "FROM comments "
        "WHERE comments.postid=:id ",
        {"id": postid_url_slug}
    )).fetchall()
    likes = (connection.execute(
        "SELECT "
        "* "
        "FROM likes "
        "WHERE likes.postid=:id ",
        {"id": postid_url_slug}
    )).fetchall()
    context['created'] = post[0]['created']
    context['imgUrl'] = '/uploads/{}'.format(post[0]['img_url'])
    context['owner'] = post[0]['owner']
    context['ownerImgUrl'] = '/uploads/{}'.format(post[0]['owner_img_url'])
    context['ownerShowUrl'] = '/users/{}/'.format(post[0]['owner'])
    context['postShowUrl'] = '/posts/{}/'.format(postid_url_slug)
    context['postid'] = postid_url_slug
    context['url'] = flask.request.path
    context['comments'] = []
    context['likes'] = {}
    for comment in comments:
        temp = {}
        temp['commentid'] = comment['commentid']
        temp['owner'] = comment['owner']
        temp['ownerShowUrl'] = '/users/{}/'.format(comment['owner'])
        temp['text'] = comment['text']
        temp['url'] = '/api/v1/comments/{}/'.format(comment['commentid'])
        if str(flask.request.authorization['username']) == comment['owner']:
            temp['lognameOwnsThis'] = True
        else:
            temp['lognameOwnsThis'] = False
        context['comments'].append(temp)
    context['likes']['lognameLikesThis'] = False
    context['likes']['url'] = None
    for like in likes:
        if str(flask.request.authorization['username']) == like['owner']:
            context['likes']['lognameLikesThis'] = True
            context['likes']['url'] = '/api/v1/likes/{}/'.format(like['likeid'])
    context['likes']['numLikes'] = len(likes)
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def add_like():
    """Add like."""
    postid_url_slug = request.args.get('postid')
    connection = insta485.model.get_db()
    context = {}
    if flask.request.authorization['username'] is None or login(connection) == 'failed':
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return flask.jsonify(**context), 403
    size = (connection.execute(
        "SELECT "
        "COUNT(postid) AS num "
        "FROM posts "
    )).fetchall()
    if int(size[0]['num']) < int(postid_url_slug):
        context['message'] = "Not found"
        context['status_code'] = 404
        return flask.jsonify(**context), 404
    likes = (connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE likes.postid=:postid ",
        {"postid": postid_url_slug}
    )).fetchall()
    usernames = []
    for like in likes:
        usernames.append(like['owner'])
    if str(flask.request.authorization['username']) in usernames:
        context['message'] = "Conflict"
        context['status_code'] = 409
        return flask.jsonify(**context), 409
    connection.execute(
        "INSERT INTO likes (owner, postid) "
        "VALUES (? , ?)", (flask.request.authorization['username'], postid_url_slug)
    )
    total_likes = (connection.execute(
        "SELECT likeid "
        "FROM likes "
    )).fetchall()
    context['likeid'] = len(total_likes)
    context['url'] = '/api/v1/likes/{}/'.format(len(total_likes))
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    connection = insta485.model.get_db()
    context = {}
    if flask.request.authorization['username'] is None or login(connection) == 'failed':
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return flask.jsonify(**context), 403
    connection.execute(
        "DELETE FROM likes "
        "WHERE likeid=:likeid",
        {"likeid": likeid}
    )
    return '', 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def add_comment():
    """Add comment."""
    postid_url_slug = request.args.get('postid')
    request_content = request.get_json()
    text = request_content['text']
    connection = insta485.model.get_db()
    context = {}
    if flask.request.authorization['username'] is None or login(connection) == 'failed':
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return flask.jsonify(**context), 403
    size = (connection.execute(
        "SELECT "
        "COUNT(postid) AS num "
        "FROM posts "
    )).fetchall()
    if int(size[0]['num']) < int(postid_url_slug):
        context['message'] = "Not found"
        context['status_code'] = 404
        return flask.jsonify(**context), 404
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (? , ? , ?)", (flask.request.authorization['username'], postid_url_slug, text)
    )
    comment = (connection.execute(
        "SELECT "
        "* "
        "FROM comments "
        "ORDER BY commentid DESC LIMIT 1 "
    )).fetchall()
    context['commentid'] = comment[0]['commentid']
    if str(flask.request.authorization['username']) == comment[0]['owner']:
        context['lognameOwnsThis'] = True
    else:
        context['lognameOwnsThis'] = False
    context['owner'] = comment[0]['owner']
    context['ownerShowUrl'] = '/users/{}/'.format(comment[0]['owner'])
    context['text'] = comment[0]['text']
    context['url'] = flask.request.path
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    connection = insta485.model.get_db()
    context = {}
    if flask.request.authorization['username'] is None or login(connection) == 'failed':
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return flask.jsonify(**context), 403
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid=:commentid",
        {"commentid": commentid}
    )
    return '', 204
