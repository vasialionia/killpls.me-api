from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config as cfg

app = Flask(__name__)
app.config.from_object(cfg)
db = SQLAlchemy(app)

import models
import views

for view in views.views:
    view.register(app)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, True)
