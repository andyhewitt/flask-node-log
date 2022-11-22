import os
import requests
from flask import Flask, render_template, request, current_app
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy.sql import func

os.environ['FLASK_DEBUG'] = 'True'

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prometheus = db.Column(db.String(100), nullable=False)
    node = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    is_current = db.Column(db.Boolean, default=False)
    Summary = db.Column(db.Text)
    histories = db.relationship('NotReadyRecord', backref='node', lazy=True)

    def __repr__(self):
        return f'<Node: {self.prometheus} {self.node}>'


class NotReadyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'),
                        nullable=False)

    def __repr__(self):
        return f'<Node: {self.node_id} {self.id}>'


def get_not_ready_list():
    params = (
        ('query',
            ''),
    )
    req = app.test_request_context()
    req.request
    response = requests.get(
        '', params=params)
    response = response.json()

    print(response)

    return response


def start_recording():
    with app.app_context():
        new_request = GetNodeStatus()
        new_request.process_node()


sched = BackgroundScheduler(daemon=True)
sched.add_job(start_recording, 'interval', minutes=0.5)
sched.start()


@app.route('/')
def index():
    nodes = Node.query.all()
    return render_template('index.html', nodes=nodes)


@app.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('nodes.html', node=node)


class GetNodeStatus():
    def __init__(self) -> None:
        self.curr = []

    def client():
        with app.test_client() as client:
            with app.app_context():  # New!!
                assert current_app.config["ENV"] == "production"
            yield client

    def get_not_ready_list(self):
        params = (
            ('query',
             ''),
        )
        response = requests.get(
            '/', params=params)
        response = response.json()

        return response

    def process_node(self):
        node_raw = self.get_not_ready_list()
        nodes_in_db = Node.query.all()

        for n in node_raw["data"]["result"]:
            node = n["metric"]["node"]
            prometheus = n["metric"]["prometheus"]
            node_exists = Node.query.filter_by(node=node).first()
            print(nodes_in_db)
            # curr_node = CurrentNodes(
            #     node=node,
            #     prometheus=prometheus,
            #     count=1,
            #     Summary="",
            # )
            # db.session.add(curr_node)
            # db.session.commit()
            new_node = Node(
                node=node,
                prometheus=prometheus,
                count=1,
                Summary="",
                is_current=True
            )
            db.session.add(new_node)
            db.session.commit()
        return self.curr

    def register_current_not_ready(self):
        node_raw = self.process_node()


class PostClients():
    def __init__(self, prometheus, node, summary) -> None:
        self.prometheus = prometheus
        self.node = node
        self.count = 1
        self.summary = ""

    def create(self):
        if request.method == 'POST':
            prometheus = self.prometheus
            node = self.node
            node = Node(prometheus=prometheus,
                        node=node,
                        count=self.count,
                        summary=self.summary)
            db.session.add(node)
            db.session.commit()

    def edit(self, node_id):
        node = Node.query.get_or_404(node_id)

        if request.method == 'POST':
            node.count = self.count + 1

            db.session.add(node)
            db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=3001)
