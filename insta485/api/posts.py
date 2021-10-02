"""REST API for posts."""
import flask
from flask import request
import insta485


@insta485.app.route('/api/v1/')
def get_services():
    """Return post on postid."""
    
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    
    # if flask.request.authorization is None:
    #    flask.abort(403)
    connection = insta485.model.get_db()
    
    context = {}
    comments = {}
    likes = {}
    
    post = (connection.execute(
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
        {"id": postid_url_slug}
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
    
    context['created'] = post[0]['timestamp']
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
        temp['url'] = flask.request.path
        
        if flask.request.authorization.get("username", None) == comment['owner']:
            temp['lognameOwnsThis'] = True
        else:
            temp['lognameOwnsThis'] = False
            
        context['comments'].append(temp)
        
    context['likes']['lognameLikesThis'] = False
    for like in likes:
        if str(flask.request.authorization['username']) == like['owner']:
            context['likes']['lognameLikesThis'] = True
    context['likes']['lognameLikesThis'] = len(likes)
    context['likes']['url'] = flask.request.path
    
    return flask.jsonify(**context)
