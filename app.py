from sqlalchemy.sql import func
import os
import re
import time
import requests
from flask import Flask, render_template, request, current_app
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from project import create_app, db
from project.api import GetNodeStatus

import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Tokyo')

os.environ['FLASK_DEBUG'] = 'True'

basedir = os.path.abspath(os.path.dirname(__file__))

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)


def start_recording():
    with app.app_context():
        new_request = GetNodeStatus()
        new_request.process_node()


sched = BackgroundScheduler(daemon=True)
sched.add_job(start_recording, 'interval', minutes=1)
sched.start()


if __name__ == '__main__':
    app.run(debug=True, port=3001)
