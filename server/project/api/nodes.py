from project.api.models import Node, Record
from project.api.reboot_client import RebootClient
from project.api import GetNodeStatus
from project import db
from flask import render_template, redirect, url_for, request, flash
import time

from flask import Blueprint

nodes_blueprint = Blueprint('nodes', __name__)


reboot_client = RebootClient()
node_client = GetNodeStatus()


@nodes_blueprint.route('/')
def index():
    nodes = Node.query.all()
    current_not_ready = Node.query.filter_by(current_not_ready=True).all()
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/refresh/')
def refresh():
    node_client.process_node()
    nodes = Node.query.all()
    current_not_ready = Node.query.filter_by(current_not_ready=True).all()
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/<int:node_id>/')
def nodes(node_id):
    node = Node.query.get_or_404(node_id)
    bmaas_url, bmaas_id = reboot_client.get_talaria_url(
        node.node.split('.')[0], node.region)
    return render_template('nodes.html', node=node, bmaas_url=bmaas_url, bmaas_id=bmaas_id)


@nodes_blueprint.route('/cluster/<string:cluster>/')
def nodes_by_prometheus(cluster):
    current_not_ready = Node.query.filter_by(
        prometheus=cluster, current_not_ready=True).all()
    nodes = Node.query.filter_by(prometheus=cluster)
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/region/<string:region>/')
def nodes_by_region(region):
    current_not_ready = Node.query.filter_by(
        region=region, current_not_ready=True).all()
    nodes = Node.query.filter_by(region=region)
    return render_template('index.html', nodes=nodes, current_not_ready=current_not_ready)


@nodes_blueprint.route('/schedulable/<string:schedulable>/')
def nodes_by_schedulable(schedulable):
    current_not_ready = Node.query.filter_by(
        schedulable=True if schedulable == "True" else False, current_not_ready=True).all()
    nodes = Node.query.filter_by(schedulable=schedulable)
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


@nodes_blueprint.route('/<int:node_id>/restart/<int:bmaas_id>/')
def restart(node_id, bmaas_id):
    node_client.process_node()
    node = Node.query.get_or_404(node_id)
    if node.schedulable == True:
        flash('Please drain the node first before operation.')
    else:
        flash(reboot_client.reboot_by_id(bmaas_id, node.region))
    return redirect(url_for('nodes.nodes', node_id=node_id))


@nodes_blueprint.route('/healthz')
def healthz():
    return "OK"


@nodes_blueprint.route('/healthx')
def healthx():
    time.sleep(1)
    return "OK"
