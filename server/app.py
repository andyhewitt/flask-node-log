from sqlalchemy.sql import func
import os
from apscheduler.schedulers.background import BackgroundScheduler
from project import create_app, db
from project.api import GetNodeStatus

import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Tokyo')

os.environ['FLASK_DEBUG'] = 'False'

app = create_app()


def start_recording():
    with app.app_context():
        new_request = GetNodeStatus()
        new_request.process_node()


if __name__ == '__main__':
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(start_recording, 'interval', minutes=1)
    sched.start()
    app.run(debug=True, port=3001)
