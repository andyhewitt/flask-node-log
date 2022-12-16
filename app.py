from sqlalchemy.sql import func
import os
import re
import time
import requests
from flask import Flask, render_template, request, current_app
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Tokyo')

datetime_ist = datetime.now(IST)
print(datetime_ist.strftime('%Y-%m-%d %H:%M:%S'))


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
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    current_not_ready = db.Column(db.Boolean, default=False, nullable=False)
    summary = db.Column(db.Text)
    histories = db.relationship('NotReadyRecord', backref='node', lazy=True)

    def __repr__(self):
        return f'<Node: {self.prometheus} {self.node}>'

    @property
    def count(self):
        return len(self.histories)

    @property
    def creation_time(self):
        dt_jp = self.created_at.astimezone(pytz.timezone('Asia/Tokyo'))
        return dt_jp.strftime("%Y-%m-%d %H:%M:%S %Z %z")


class NotReadyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'),
                        nullable=False)

    def __repr__(self):
        return f'<Node: {self.node_id} {self.id}>'

    @property
    def creation_time(self):
        dt_jp = self.created_at.astimezone(pytz.timezone('Asia/Tokyo'))
        return dt_jp.strftime("%Y-%m-%d %H:%M:%S %Z %z")


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
    current_not_ready = Node.query.filter_by(current_not_ready=True).all()
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@app.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('nodes.html', node=node)


@app.route('/healthz')
def healthz():
    return "OK"


@app.route('/healthx')
def healthx():
    time.sleep(1)
    return "OK"


class GetNodeStatus():
    def client():
        with app.test_client() as client:
            with app.app_context():  # New!!
                assert current_app.config["ENV"] == "production"
            yield client

    def get_not_ready_list(self):
        params = (
            ('query',
             'kube_node_status_condition{condition="Ready",prometheus=~".*[0-9]-k8s-v2.*",status="true"}==0'),
        )
        response = requests.get(
            'https://caas.mon-aas-api.r-local.net/prometheus/api/v1/query', params=params)
        response = response.json()

        return response["data"]["result"]

    def process_node(self):
        new_nr_node = self.get_not_ready_list()
        new_nr_node_list = []
        for new_list in new_nr_node:
            new_nr_node_list.append(new_list["metric"]["node"])

        # Get all the current not ready nodes on last check
        prev_not_ready = Node.query.filter_by(current_not_ready=True).all()
        # Step 1, update current not ready node.
        for new_node in new_nr_node:
            new_entered_node = new_node["metric"]["node"]
            # new_entered_node_prometheus = new_node["metric"]["prometheus"]
            # print(new_entered_node_prometheus)
            new_entered_node_prometheus = re.search(r'([a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9])', new_node["metric"]["prometheus"]).group(1)
            

            # Check if this node is already in the database and is currently not ready.
            is_current_notready = Node.query.filter_by(
                current_not_ready=True, node=new_entered_node).first()

            # Check if this node is in the database
            is_not_ready_and_existing = Node.query.filter_by(
                node=new_entered_node).first()

            # If this node is currently not ready, ignore
            if is_current_notready is not None:
                # Ignore this one because it is a ongoing alert
                print("Still ongoing", is_current_notready.node)
            # Else, update db if db has record, or create a new record
            else:
                if is_not_ready_and_existing is not None:
                    print("Existing ", new_entered_node)
                    is_not_ready_and_existing.current_not_ready = True
                    record = NotReadyRecord(node=is_not_ready_and_existing)
                    db.session.add(is_not_ready_and_existing)
                    db.session.add(record)
                    db.session.commit()
                else:
                    print("New node", new_entered_node)
                    new_node = Node(
                        node=new_entered_node,
                        prometheus=new_entered_node_prometheus,
                        summary="",
                        current_not_ready=True
                    )
                    record = NotReadyRecord(node=new_node)
                    db.session.add(new_node)
                    db.session.add(record)
                    db.session.commit()

        # Set resolved node to false and also update record
        # print(new_nr_node_list)
        for cr_node in prev_not_ready:
            if cr_node.node not in new_nr_node_list:
                print("Resolved ", cr_node.node)
                cr_node.current_not_ready = False
                db.session.add(cr_node)
                db.session.commit()

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
