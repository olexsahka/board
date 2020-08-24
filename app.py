import os
import secrets

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, current_app
import datetime
from flask_login import LoginManager, UserMixin
from flask_moment import Moment

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager=LoginManager(app)
class msg(db.Model):
    id=db.Column( db.Integer,primary_key=True)
    current_id=db.Column(db.Integer ,nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'))
    msgDate=db.Column(db.DateTime)
    msg=db.Column(db.Text)
    post=db.relationship('Post')

class User(db.Model, UserMixin):
    #__tablename__ = "users"
    id=db.Column( db.Integer,primary_key=True)
    mail=db.Column(db.String(200), unique=True,nullable=False)
    name=db.Column(db.String(200), nullable=False)
    id_vk=db.Column(db.String(200), unique=True,nullable=False)
    hostel=db.Column(db.String(100), nullable=False)
    password=db.Column(db.String(200), nullable=False)



class Post(db.Model):
   # __tablename__ = "posts"
    id=db.Column(db.Integer,primary_key=True,unique=True)
    name = db.Column(db.String(200), nullable=False)
    description=db.Column(db.String(1000),nullable=False)
    category=db.Column(db.String(100),nullable=False)
    cost=db.Column(db.Integer,nullable=False)
    hostel=db.Column(db.String(100),nullable=False)
    urlon=db.Column(db.String(1000),nullable=False)
    timestamp = db.Column(db.DateTime)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    active=db.Column(db.Boolean())
    user=db.relationship('User')
    img_0 = db.Column(db.String(120), default='image.jpg')
    img_1 = db.Column(db.String(120), default='image.jpg')
    img_2 = db.Column(db.String(120), default='image.jpg')
    img_3 = db.Column(db.String(120), default='image.jpg')


def save_img(photo):

    hash_photo = secrets.token_urlsafe(10)
    _, file_extention = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extention
    file_path = os.path.join(current_app.root_path, 'static/img', photo_name)
    photo.save(file_path)
    return photo_name



  #  def __init__(self, description, name, category, hostel, cost,pub_date,urlon):
    #    self.description = description
      #  self.name = name
      #  self.category = category
      #  self.hostel = hostel
      #  self.cost = cost
     #   self.urlon=urlon




   # def __repr__(self):
   #     return '<Post %r>' % self.id




@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
import routes

