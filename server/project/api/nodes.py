from project.api.models import Node, Record
from project import db
from flask import render_template, redirect, url_for, request
import time

from flask import Blueprint

nodes_blueprint = Blueprint('nodes', __name__)


@nodes_blueprint.route('/')
def index():
    nodes = Node.query.all()
    current_not_ready = Node.query.filter_by(current_not_ready=True).all()
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('nodes.html', node=node)


@nodes_blueprint.route('/<string:prometheus_region>/')
def nodes_by_prometheus(prometheus_region):
    current_not_ready = Node.query.filter_by(
        prometheus=prometheus_region, current_not_ready=True).all()
    nodes = Node.query.filter_by(prometheus=prometheus_region)
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/<int:node_id>/<int:record_id>/delete/')
def delete(node_id, record_id):
    record = Record.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('nodes.nodes', node_id=node_id))


@nodes_blueprint.route('/<int:node_id>/reported/')
def reported(node_id):
    node = Node.query.get_or_404(node_id)
    node.reported = not node.reported
    db.session.commit()
    return redirect(url_for('nodes.index'))


@nodes_blueprint.route('/<int:node_id>/summary/', methods=('GET', 'POST'))
def summary(node_id):
    node = Node.query.get_or_404(node_id)
    if request.method == 'POST':
        summary = request.form['summary']
        node.summary = summary
        db.session.commit()

        return redirect(url_for('nodes.nodes', node_id=node_id))


@nodes_blueprint.route('/healthz')
def healthz():
    return "OK"


@nodes_blueprint.route('/healthx')
def healthx():
    time.sleep(1)
    return "OK"
