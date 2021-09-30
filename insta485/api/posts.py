"""REST API for posts."""
import flask
import insta485


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.



    another one
    {
  "comments": [
    {
      "commentid": 1,
      "lognameOwnsThis": true,
      "owner": "awdeorio",
      "ownerShowUrl": "/users/awdeorio/",
      "text": "#chickensofinstagram",
      "url": "/api/v1/comments/1/"
    },
    {
      "commentid": 2,
      "lognameOwnsThis": false,
      "owner": "jflinn",
      "ownerShowUrl": "/users/jflinn/",
      "text": "I <3 chickens",
      "url": "/api/v1/comments/2/"
    },
    {
      "commentid": 3,
      "lognameOwnsThis": false,
      "owner": "michjc",
      "ownerShowUrl": "/users/michjc/",
      "text": "Cute overload!",
      "url": "/api/v1/comments/3/"
    }
  ],
  "created": "2021-05-06 19:52:44",
  "imgUrl": "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg",
  "likes": {
    "lognameLikesThis": true,
    "numLikes": 1,
    "url": "/api/v1/likes/6/"
  },
  "owner": "awdeorio",
  "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
  "ownerShowUrl": "/users/awdeorio/",
  "postShowUrl": "/posts/3/",
  "postid": 3,
  "url": "/api/v1/posts/3/"
    }
    """
    
    if not 'username' in flask.session:
        flask.abort(403)
        
    context = {}
    
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
        {"id": postid_url_slug}
    )).fetchall()
    
    
    
    context = {
        "age": "2017-09-28 04:33:28",
        "img_url": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "owner_img_url": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "owner_show_url": "/users/awdeorio/",
        "postid": "/posts/{}/".format(postid_url_slug),
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
