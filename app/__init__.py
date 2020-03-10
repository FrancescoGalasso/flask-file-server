from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app_file_server = Flask(__name__)
app_file_server.config.from_object(Config)
db = SQLAlchemy(app_file_server)
login = LoginManager(app_file_server)
login.login_view = 'login'

from app import routes, models

# Create DB with a test user if DB does not exist
from pathlib import Path
import pathlib
parent_dir = Path(__file__).parent.parent
DB_PATH = parent_dir / 'file_server.db'

if not DB_PATH.exists():
	from werkzeug.security import generate_password_hash
	from datetime import datetime
	import os

	print('CREATING SAMPLE DB')
	# create tables
	db.create_all()

	# create test_user
	test_user = models.User(username='test', email='test@example.com', password_hash=generate_password_hash('test'))
	db.session.add(test_user)
	db.session.commit()

	# create itemfiles
	file_author = models.User.query.get(1)
	file_data_1 = "This is a test file 1 !!!".encode()	#bytes
	file_data_2 = "This is a test file 2 !!!".encode()	#bytes


	item_file_1 = models.ItemFile(filename='test_file_1.txt', data=file_data_1, creation_time=datetime.utcnow(), modification_time=datetime.utcnow(), author=file_author)
	item_file_2 = models.ItemFile(filename='test_file_2.txt', data=file_data_2, creation_time=datetime.utcnow(), modification_time=datetime.utcnow(), author=file_author)
	
	db.session.add(item_file_1)
	db.session.add(item_file_2)
	db.session.commit()

