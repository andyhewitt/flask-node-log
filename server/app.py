from apscheduler.schedulers.background import BackgroundScheduler
from project import create_app
from project.api import GetNodeStatus

import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Tokyo')

app = create_app()


def start_recording():
    with app.app_context():
        new_request = GetNodeStatus()
        new_request.process_node()


sched = BackgroundScheduler(daemon=True)
sched.add_job(start_recording, 'interval', minutes=0.5)
sched.start()

if __name__ == '__main__':
    app.run(debug=True, port=3001)
