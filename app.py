import os,time
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

os.environ['FLASK_DEBUG'] = 'True'

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

node = [
	"jpe2-caas1-prod1-node-000001",
	"jpe2-caas1-prod1-node-000002",
	"jpe2-caas1-prod1-node-000003",
	"jpe2-caas1-prod1-node-000004",
	"jpe2-caas1-prod1-node-000005",
	"jpe2-caas1-prod1-node-000006",
	"jpe2-caas1-prod1-node-000007",
]



class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prometheus = db.Column(db.String(100), nullable=False)
    node = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    Summary = db.Column(db.Text)
    histories = db.relationship('NotReadyRecord', backref='node', lazy=True)


    def __repr__(self):
        return f'<Node: {self.prometheus} {self.node}>'

def addNodeRecords():
    db.create_all()
    for i in node:
        _node = Node(
            node=i,
            prometheus=f"jpe2-caas1-prod1",
            count=1,
            Summary="First time",
        )
        db.session.add(_node)
        db.session.commit()


class NotReadyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                        server_default=func.now())
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'),
        nullable=False)

    def __repr__(self):
        return f'<Node: {self.node_id} {self.id}>'



@app.route('/')
def index():
    nodes = Node.query.all()
    return render_template('index.html', nodes=nodes)


@app.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('nodes.html', node=node)


# @app.route('/create/', methods=('GET', 'POST'))
class PostClients():
    def __init__(self, prometheus, node,summary) -> None:
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
