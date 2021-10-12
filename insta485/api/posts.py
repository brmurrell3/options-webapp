"""REST API for posts."""
import hashlib
import flask
from flask import request
import insta485


def encrypt(base_input, salt):
    """Encrypt."""
    algorithm = 'sha512'
    hash_object = hashlib.new(algorithm)
    password_salted = salt + base_input
    hash_object.update(password_salted.encode('utf-8'))
    password_hash = hash_object.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def login(connection):
    """Check credentials."""
    if flask.request.authorization is not None:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
    elif (request.form.get('username') is not None
            and request.form.get('password') is not None
            and request.form.get('username') == 'login'):
        username = request.form.get('username')
        password = request.form.get('password')
    elif 'username' in flask.session:
        return flask.session['username']
    else:
        context = {}
        context['message'] = "Forbidden"
        context['status_code'] = 403
        return context
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
    if dbpass == encrypt(password, dbsalt):
        return username
    context = {}
    context['message'] = "Forbidden"
    context['status_code'] = 403
    return context


def post_info(connection, postid_url_slug, logname):
    """Return post on postid."""
    context = {}
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
    context['imgUrl'] = '/uploads/' + str(post[0]['img_url'])
    context['owner'] = post[0]['owner']
    context['ownerImgUrl'] = '/uploads/' + str(post[0]['owner_img_url'])
    context['ownerShowUrl'] = '/users/' + str(post[0]['owner']) + '/'
    context['postShowUrl'] = f'/posts/{postid_url_slug}/'
    context['postid'] = postid_url_slug
    context['url'] = flask.request.path
    context['comments'] = []
    context['likes'] = {}
    for comment in comments:
        temp = {}
        temp['commentid'] = comment['commentid']
        temp['owner'] = comment['owner']
        temp['ownerShowUrl'] = '/users/' + str(comment['owner']) + '/'
        temp['text'] = comment['text']
        temp['url'] = '/api/v1/comments/' + str(comment['commentid']) + '/'
        if str(logname) == comment['owner']:
            temp['lognameOwnsThis'] = True
        else:
            temp['lognameOwnsThis'] = False
        context['comments'].append(temp)
    context['likes']['lognameLikesThis'] = False
    context['likes']['url'] = None
    for like in likes:
        if str(logname) == like['owner']:
            context['likes']['lognameLikesThis'] = True
            context['likes']['url'] = '/api/v1/likes/' + str(
                        like['likeid']) + '/'
    context['likes']['numLikes'] = len(likes)
    return context


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


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_posts():
    """Return 10 newest posts."""
    context = {}
    connection = insta485.model.get_db()
    logname = login(connection)
    # checking if user is authenticated
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
    # getting size and page from args
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page',
                                  default=0, type=int)  # pages 0 indexed
    page_offset = page * size
    # error checking
    if size < 0 or page < 0:
        context['message'] = 'Bad Request'
        context['status_code'] = 400
        return flask.jsonify(**context), 400
    # getting all the posts, setting a limit if necessary
    if request.args.get('postid_lte') is None:
        # setting the postid_lte since it doesn't exist
        total_posts = (connection.execute(
            "SELECT "
            "MAX(postid) AS max "
            "FROM posts "
        )).fetchall()
        lte = total_posts[0]['max']
        # getting all the posts on the page
        get_page = (connection.execute(
            "SELECT "
            "postid, "
            "owner "
            "FROM posts "
            "WHERE owner = ? OR owner IN "
            "(SELECT username2 FROM following WHERE username1 = ?) "
            "ORDER BY postid DESC "
            "LIMIT ? OFFSET ? ",
            (logname, logname, size, page_offset)
        )).fetchall()
    else:
        lte = int(request.args.get('postid_lte'))
        # getting all the posts on the page
        get_page = (connection.execute(
            "SELECT "
            "postid, "
            "owner "
            "FROM posts "
            "WHERE (owner = ? OR owner IN "
            "(SELECT username2 FROM following WHERE username1 = ?)) "
            "AND postid <= ? "
            "ORDER BY postid DESC "
            "LIMIT ? OFFSET ? ",
            (logname, logname, lte, size, page_offset)
        )).fetchall()
    # populating context dictionary with results
    context['results'] = []
    for post in get_page:
        post_context = post_info(connection, int(post['postid']), logname)
        post_context['url'] = '/api/v1/posts/' + str(post['postid']) + '/'
        context['results'].append(post_context)
    # calculating current url
    context['url'] = flask.request.path
    index = 0
    for arg in request.args:
        if index == 0:
            context['url'] = (context['url'] + '?' + arg + '=' +
                              str(flask.request.args.get(arg)))
        else:
            context['url'] = (context['url'] + '&' + arg + '=' +
                              str(flask.request.args.get(arg)))
        index += 1
    # calculating the next url
    if len(get_page) < size:
        context['next'] = ""
    else:
        context['next'] = (flask.request.path + '?size=' + str(size) + '&page='
                           + str(page + 1) + '&postid_lte=' + str(lte))
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Get information about a post."""
    connection = insta485.model.get_db()
    logname = login(connection)
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
    size = (connection.execute(
        "SELECT "
        "COUNT(postid) AS num "
        "FROM posts "
    )).fetchall()
    if int(size[0]['num']) < int(postid_url_slug):
        context = {}
        context['message'] = "Not found"
        context['status_code'] = 404
        return flask.jsonify(**context), 404
    context = post_info(connection, postid_url_slug, logname)
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def add_like():
    """Add like."""
    postid_url_slug = request.args.get('postid')
    connection = insta485.model.get_db()
    context = {}
    logname = login(connection)
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
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
    if str(logname) in usernames:
        context['message'] = "Conflict"
        context['status_code'] = 409
        return flask.jsonify(**context), 409
    connection.execute(
        "INSERT INTO likes (owner, postid) "
        "VALUES (? , ?)",
        (logname, postid_url_slug)
    )
    total_likes = (connection.execute(
        "SELECT "
        "MAX(likeid) AS max "
        "FROM likes "
    )).fetchall()
    context['likeid'] = total_likes[0]['max']
    context['url'] = '/api/v1/likes/' + str(total_likes[0]['max']) + '/'
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete a like."""
    connection = insta485.model.get_db()
    logname = login(connection)
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
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
    logname = login(connection)
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
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
        "VALUES (? , ? , ?)",
        (logname, postid_url_slug, text)
    )
    comment = (connection.execute(
        "SELECT "
        "* "
        "FROM comments "
        "ORDER BY commentid DESC LIMIT 1 "
    )).fetchall()
    context['commentid'] = comment[0]['commentid']
    if str(logname) == comment[0]['owner']:
        context['lognameOwnsThis'] = True
    else:
        context['lognameOwnsThis'] = False
    context['owner'] = comment[0]['owner']
    context['ownerShowUrl'] = '/users/' + str(comment[0]['owner']) + '/'
    context['text'] = comment[0]['text']
    context['url'] = flask.request.path
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    connection = insta485.model.get_db()
    logname = login(connection)
    if isinstance(logname, dict):
        return flask.jsonify(**logname), 403
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid=:commentid",
        {"commentid": commentid}
    )
    return '', 204
