from project import db
from sqlalchemy.sql import func
import pytz


class Node(db.Model):

    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    prometheus = db.Column(db.String(100), nullable=False)
    node = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    current_not_ready = db.Column(db.Boolean, default=False, nullable=False)
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
    # nodes = db.relationship('Node', back_populates="records", lazy=True)

    def __repr__(self):
        return f'<Node: {self.node_id} {self.id}>'

    @property
    def creation_time(self):
        dt_jp = self.created_at.astimezone(pytz.timezone('Asia/Tokyo'))
        return dt_jp.strftime("%Y-%m-%d %H:%M:%S %Z %z")
