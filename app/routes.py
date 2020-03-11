from flask import render_template, flash, redirect, url_for, request, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app_file_server, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, ItemFile, PLATFORMS, TYPE_FILES
from datetime import datetime

import io

@app_file_server.route('/')
@app_file_server.route('/index')
@login_required
def index():
	doc_files = ItemFile.query.filter_by(file_type='doc')
	prog_files = ItemFile.query.filter_by(file_type='prog')
	return render_template('index.html', doc_files=doc_files, prog_files=prog_files)


@app_file_server.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@app_file_server.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app_file_server.route('/register', methods=['GET', 'POST'])
def register():
	# if current_user.is_authenticated:
	# 	return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app_file_server.route('/download/<int:file_id>')
@login_required
def download(file_id):
	obj = ItemFile.query.filter_by(id=file_id).first()
	print('file_id: {} | file: {}'.format(file_id, obj.serialized))

	from io import BytesIO
	return send_file(BytesIO(obj.data), attachment_filename=obj.filename, as_attachment=True)

@app_file_server.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	if not current_user.is_admin():
		return redirect(url_for('index'))
	
	if request.method == 'POST':
		file = request.files['inputFile']
		result = request.form

		file_description = result['upload_description']
		file_platform = result.get('upload_platform')
		file_type = result.get('upload_file_type')

		newFile = ItemFile(filename=file.filename,
							data=file.read(),
							creation_time=datetime.utcnow(), 
							modification_time=datetime.utcnow(),
							file_description=file_description,
							platform=file_platform,
							file_type=file_type)
		db.session.add(newFile)
		db.session.commit()
		flash('Saved ' + file.filename + ' into DB!')
		return redirect(url_for('index'))
	else:
		return render_template('upload.html', platforms=PLATFORMS, file_types=TYPE_FILES)

