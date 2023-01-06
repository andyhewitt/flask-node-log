from project.api.models import Node
from project import app
from flask import render_template
import time


@app.route('/')
def index():
    nodes = Node.query.all()
    current_not_ready = Node.query.filter_by(current_not_ready=True).all()
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@app.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('nodes.html', node=node)


@app.route('/<string:prometheus_region>/')
def nodes_by_prometheus(prometheus_region):
    current_not_ready = Node.query.filter_by(
        prometheus=prometheus_region, current_not_ready=True).all()
    nodes = Node.query.filter_by(prometheus=prometheus_region)
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@app.route('/healthz')
def healthz():
    return "OK"


@app.route('/healthx')
def healthx():
    time.sleep(1)
    return "OK"
