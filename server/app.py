from apscheduler.schedulers.background import BackgroundScheduler
from project import create_app
from project.api import GetNodeStatus


app = create_app()


def start_recording():
    with app.app_context():
        new_request = GetNodeStatus()
        new_request.process_node('qa')
        new_request.process_node('prod')


sched = BackgroundScheduler(daemon=True)
sched.add_job(start_recording, 'interval', minutes=200)
sched.start()

if __name__ == '__main__':
    app.run(debug=True, port=3001)
