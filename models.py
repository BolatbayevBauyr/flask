# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from app import db

from app.base.util import hash_pass
from functools import wraps
import logging

from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:

  def start_session(self, user):
    
    session['logged_in'] = True
    session['user'] = user['username']
    return session['user']

  def signup(self, username, email, password):
    print(request.form)

    # Create the user object
    user = {
      "username": username,
      "email": email,
      "password": password
    }
    

    # Encrypt the password
    user['hashed_password'] = pwd_context.hash((user['password'])) 

    if db.users.insert_one(user):
        return True
    return False


  
  def logout(self):
    session.clear()
    return redirect('/')
  
  def login(self, username, password):

    user = db.users.find_one({
      "username": username
    })
    logging.error(user)

    if user and pwd_context.verify(password, user['hashed_password']):
      self.start_session(user)
      return True
    return False


def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

    

