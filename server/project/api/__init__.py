from project.api.models import Node, Record
from project import db
import requests
import re
import logging


class GetNodeStatus():
    def get_not_ready_list(self, env):
        params = (
            ('query',
             'sum by (node, prometheus) (kube_node_status_condition{condition="Ready",prometheus=~".*[0-9]-k8s.*",status="true"}==0) + on(node, prometheus) kube_node_spec_unschedulable'),
        )
        mon_aas_url = 'https://caas.mon-aas-api.r-local.net/prometheus/api/v1/query' if env == "prod" else 'https://caas.qa-mon-aas-api.r-local.net/prometheus/api/v1/query'
        response = requests.get(
            mon_aas_url, params=params)
        response = response.json()

        return response["data"]["result"]

    def process_node(self, env):
        new_notready_nodes = self.get_not_ready_list(env)
        new_notready_nodes_list = {
            'qa': [],
            'prod': []
        }
        for new_list in new_notready_nodes:
            new_notready_nodes_list[env].append(new_list["metric"]["node"])

        # Get all the not ready nodes on last check
        prev_not_ready = Node.query.filter_by(
            current_not_ready=True, env=env).all()
        # Set resolved node to false and also update record
        for prev_node in prev_not_ready:
            if prev_node.node not in new_notready_nodes_list[env]:
                logging.info(f"Resolved {prev_node.node}")
                prev_node.current_not_ready = False
                db.session.add(prev_node)
                db.session.commit()

        # Step 1, update current not ready node.
        for new_node in new_notready_nodes:
            new_entered_node = new_node["metric"]["node"]
            region = new_entered_node.split('.')[2]

            new_entered_node_prometheus = re.search(
                r'([a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9]{1}-[a-z]{1,}[0-9])', new_node["metric"]["prometheus"]).group(1)
            scheduling_status = False if new_node["value"][1] == "1" else True

            # Check last status, if this node is already in the database and is currently not ready.
            is_in_db_and_current_notready = Node.query.filter_by(
                current_not_ready=True, node=new_entered_node, env=env).first()

            # Check if this node is in the database
            is_in_db = Node.query.filter_by(
                node=new_entered_node, env=env).first()

            # If this node is currently not ready, update scheduling status and ignore
            if is_in_db_and_current_notready is not None:
                logging.info(
                    f"Still ongoing {is_in_db_and_current_notready.node}")
                if is_in_db_and_current_notready.schedulable != scheduling_status:
                    is_in_db_and_current_notready.schedulable = scheduling_status
                    db.session.commit()
            # If it resolved, update db if db has record of it, or create a new record.
            else:
                if is_in_db is not None:
                    logging.info(f"Existing {new_entered_node}")
                    is_in_db.current_not_ready = True
                    if is_in_db.schedulable != scheduling_status:
                        is_in_db.schedulable = scheduling_status
                    record = Record(nodes=is_in_db)
                    db.session.add(is_in_db)
                    db.session.add(record)
                    db.session.commit()
                else:
                    logging.info(f"New node {new_entered_node}")
                    new_node = Node(
                        node=new_entered_node,
                        region=region,
                        env=env,
                        schedulable=scheduling_status,
                        prometheus=new_entered_node_prometheus,
                        summary="",
                        current_not_ready=True
                    )
                    record = Record(nodes=new_node)
                    db.session.add(new_node)
                    db.session.add(record)
                    db.session.commit()

        return f'Successfully get {env} status.'
