from app import db, Node
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

os.environ['FLASK_DEBUG'] = 'True'

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

node = [
	"jpe2-caas1-prod1-node-000001"
	"jpe2-caas1-prod1-node-000002"
	"jpe2-caas1-prod1-node-000003"
	"jpe2-caas1-prod1-node-000004"
	"jpe2-caas1-prod1-node-000005"
	"jpe2-caas1-prod1-node-000006"
	"jpe2-caas1-prod1-node-000007"
]

def addNodeRecords():
	db.create_all()
	for i in node:
		node_1 = Node(
			prometheus="jpe2-caas1-prod1",
			node=i,
			count=1,
			Summary="First time"
		)
		db.session.add(node_1)
	db.session.commit()