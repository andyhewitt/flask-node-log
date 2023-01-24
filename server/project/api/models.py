from project import db
from sqlalchemy.sql import func
import pytz

import ldap3
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms import validators

from ldap3 import Server, Connection, ALL

# from project import create_app

# app = create_app()


def get_ldap_connection():
    conn = ldap3.initialize('ldap://ldap.forumsys.com:389/')
    return conn


class Node(db.Model):

    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    prometheus = db.Column(db.String(100), nullable=False)
    node = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    current_not_ready = db.Column(db.Boolean, default=False, nullable=False)
    reported = db.Column(db.Boolean, default=False, nullable=False)
    schedulable = db.Column(db.Boolean, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    env = db.Column(db.String(20), nullable=False)
    summary = db.Column(db.Text)
    records = db.relationship('Record', backref="nodes", lazy=True)

    def __repr__(self):
        return f'<Node: {self.prometheus} {self.node}>'

    @property
    def count(self):
        return len(self.records)

    @property
    def creation_time(self):
        dt_jp = self.created_at.astimezone(pytz.timezone('Asia/Tokyo'))
        return dt_jp.strftime("%Y-%m-%d %H:%M:%S %Z %z")


class Record(db.Model):

    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'),
                        nullable=False)

    def __repr__(self):
        return f'<Node: {self.node_id} {self.id}>'

    @property
    def creation_time(self):
        dt_jp = self.created_at.astimezone(pytz.timezone('Asia/Tokyo'))
        return dt_jp.strftime("%Y-%m-%d %H:%M:%S %Z %z")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username

    @staticmethod
    def try_login(username, password):
        server = Server('ldap.forumsys.com', get_info=ALL)
        Connection(server, 'uid={username},dc=example,dc=com'.format(
            username=username), password, auto_bind=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
