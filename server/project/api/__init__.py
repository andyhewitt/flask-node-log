from flask import request
from project.api.models import Node, Record
from project import db, create_app
import requests
import re

app = create_app()


class GetNodeStatus():

    def get_not_ready_list(self):
        params = (
            ('query',
             'kube_node_status_condition{condition="Ready",prometheus=~".*[0-9]-k8s-v2.*",status="true"}==0'),
        )
        response = requests.get(
            'http://localhost:3000/sample', params=params)
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
            new_entered_node_prometheus = re.search(
                r'([a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9])', new_node["metric"]["prometheus"]).group(1)

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
                    record = Record(nodes=is_not_ready_and_existing)
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
                    record = Record(nodes=new_node)
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
