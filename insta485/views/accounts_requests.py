"""Login."""

import os
import hashlib
import pathlib
import uuid
import flask
from flask import request, abort
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


@insta485.app.route('/accounts/', methods=['POST'])
def account():
    """Account."""
    connection = insta485.model.get_db()
    url = request.args.get('target')
    if url is None:
        url = '/'
    # logname = flask.session['username']
    operation = request.form.get('operation')
    if operation == 'login':
        # Use username and password from the POST
        # request form content to log the user in.
        login(connection)

    elif operation == 'create':
        # Use username, password, fullname, email and file
        # from the POST request form content to create the
        # user. See above for file upload and naming procedure.
        create(connection)
        # Log the user in and redirect to URL.

    elif operation == 'delete':
        # If the user is not logged in, abort(403).
        return delete(connection, url)

    elif operation == 'edit_account':
        # If the user is not logged in, abort(403).
        return edit_account(connection)
    elif operation == 'update_password':
        # If the user is not logged in, abort(403).
        return update_password(connection)

    return flask.redirect(url)


def update_password(connection):
    """Operation update_password."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        abort(403)
    url = request.args.get('target')

    # Use password, new_password1 and new_password2
    # from the POST request form content to update
    # the user’s password.
    password = request.form.get('password')
    new_password1 = request.form.get('new_password1')
    new_password2 = request.form.get('new_password2')

    # If any of the above fields are empty, abort(400).
    if password is None:
        abort(400)
    if new_password1 is None:
        abort(400)
    if new_password2 is None:
        abort(400)
    if password == "":
        abort(400)
    if new_password1 == "":
        abort(400)
    if new_password2 == "":
        abort(400)

    # Verify password against the user’s password hash
    # in the database.
    logname = flask.session['username']

    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username=:username ",
        {"username": logname}
    )
    data = cur.fetchall()
    # print("PRINTING DATA")
    # print(data)
    # print("END OF DATA PRINT")

    dbpass = data[0]['password']
    dbsalt = (dbpass.split('$'))[1]

    # If verification fails, abort(403).
    if dbpass != encrypt(password, dbsalt):
        print("password is wrong")
        abort(403)

    # Verify both new passwords match.
    # If verification fails, abort(401).
    if new_password1 != new_password2:
        print("passwords do not match")
        abort(401)

    # Update hashed password entry in
    # database. See above for the
    # password storage procedure.
    connection.execute(
        "UPDATE users "
        "SET password=:fullname "
        "WHERE username=:username",
        {"fullname": encrypt(new_password1, dbsalt), "username": logname}
    )

    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username=:username ",
        {"username": logname}
    )
    data = cur.fetchall()
    print("printing updated table data")
    print(data)
    print("end of printing udated table")

    # Redirect to URL.
    return flask.redirect(url)


def edit_account(connection):
    """Operation edit_account."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        abort(403)

    # Use fullname, email and file from the
    # POST request form content to edit the
    # user account.
    url = request.args.get('target')
    logname = flask.session['username']
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    username = logname

    # If the fullname or email fields are empty, abort(400).
    if (fullname is None) or (email is None):
        abort(400)

    # Unpack flask object
    zfileobj = flask.request.files['file']

    # if no photo file is included, update only the
    # user’s name and email.
    if zfileobj is None:
        connection.execute(
            "UPDATE users "
            "SET fullname=:fullname, email=:email "
            "WHERE username=:username",
            {"fullname": fullname, "email": email, "username": username})
    # If a photo file is included, then the server will update
    # the user’s photo, name and email.
    else:
        zfilename = zfileobj.filename
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(zfilename).suffix
        )
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        zfileobj.save(path)

        oldfile = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=:username ",
            {"username": username}
        ).fetchall()
        connection.execute(
            "UPDATE users "
            "SET fullname=:fullname, email=:email, filename=:filename "
            "WHERE username=:username",
            {"fullname": fullname, "email": email,
                "filename": uuid_basename, "username": username})
        # Delete the old photo from the filesystem. See above for
        # file upload and naming procedure.
        os.remove(
            insta485.app.config["UPLOAD_FOLDER"]/oldfile[0]['filename'])
    # Upon successful submission, redirect to URL.
    return flask.redirect(url)


def delete(connection, url):
    """Operation delete."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        abort(403)
    logname = flask.session['username']

    # Delete all post files created by this user.
    posts = (connection.execute(
        "SELECT "
        "filename "
        "FROM posts "
        "WHERE owner=:owner ",
        {"owner": logname}
    )).fetchall()

    for post in posts:
        print(post)
        os.remove(insta485.app.config["UPLOAD_FOLDER"]/post['filename'])

    # Delete user icon file.
    profile_picture = (connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username=:username ",
        {"username": logname}
        )).fetchall()
    os.remove(
        insta485.app.config[
            "UPLOAD_FOLDER"]/profile_picture[0]['filename'])

    # Delete all related entries in all tables.
    connection.execute(
        "DELETE FROM users "
        "WHERE username=:logname",
        {"logname": logname}
    )

    flask.session.clear()
    # Log the user in and redirect to URL.
    return flask.redirect(url)


def create(connection):
    """Operation create."""
    # Use username, password, fullname, email and file
    # from the POST request form content to create the
    # user. See above for file upload and naming procedure.
    username = request.form.get('username')
    password = encrypt(request.form.get('password'), uuid.uuid4().hex)
    fullname = request.form.get('fullname')
    email = request.form.get('email')

    # If any of the above fields are empty, abort(400).
    if username is None or password is None:
        abort(400)
    if fullname is None or email is None:
        abort(400)
    if username == "" or password == "":
        abort(400)
    if fullname == "" or email == "":
        abort(400)

    # If a user tries to create an account with an
    # existing username in the database, abort(409).
    # 409 is the HTTP code indicating a Conflict Error.
    existing_usernames = (
        connection.execute("SELECT users.username from users")
        ).fetchall()
    for row in existing_usernames:
        if row['username'] == username:
            abort(409)

    afileobj = flask.request.files['file']
    afilename = afileobj.filename

    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(afilename).suffix
    )

    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    afileobj.save(path)
    if os.stat(path).st_size == 0:
        abort(400)
    connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES ( ?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password)
    )
    flask.session['username'] = username
    # Log the user in and redirect to URL.


def login(connection):
    """Operation login."""
    # Use username and password from the POST
    # request form content to log the user in.
    username = request.form.get('username')
    password = request.form.get('password')

    # If the username or password fields are empty, abort(400).
    if username is None or password is None:
        abort(400)
    if username == "" or password == "":
        abort(400)

    cur = connection.execute(
        "SELECT DISTINCT username, password "
        "FROM users WHERE username=:temp ",
        {'temp': str(username)}
    )
    data = cur.fetchall()
    # If username and password authentication fails, abort(403).
    if not data:  # the username search returned null
        abort(403)

    dbuser = data[0]['username']
    dbpass = data[0]['password']
    dbsalt = (dbpass.split('$'))[1]

    # If username and password authentication fails, abort(403).
    if dbpass != encrypt(password, dbsalt):
        abort(403)
    flask.session['username'] = dbuser
