"""Login."""

import hashlib
# import pathlib
# import uuid
# import os
# import flask
# from flask import request
# import insta485


def encrypt(input_in, salt):
    """Encrypt."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_in
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string
