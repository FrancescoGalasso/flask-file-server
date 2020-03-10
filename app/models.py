from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


# models.User
ROLES = {
    'admin': 0,
    'tech_manager': 1,
    'user': 2,
    'guest': 3
}

# models.ItemFile
PLATFORM = {
    'win32': 'Windows x86',
    'win64': 'Windows x64'
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    item_file = db.relationship('ItemFile', backref='author', lazy='dynamic')
    access = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def show_access(self):
        return self.access

    def is_admin(self):
        return self.access == ROLES['admin']

    @property
    def serialized(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'passwd': self.password_hash,
        }

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class ItemFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), index=True, unique=True)
    data = db.Column(db.LargeBinary) # blob type into sqlite
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    modification_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_description = db.Column(db.String(240))
    platform = db.Column(db.String(120))

    def __repr__(self):
        return '<ItemFile {}>'.format(self.filename)

    @property
    def serialized(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'filename': self.filename,
            'user_id': self.user_id,
            'creation_time': self.creation_time,
        }

    @property
    def str_time(self):
        return self.creation_time.strftime('%B %d %Y')

    @property
    def show_platform(self):
        if self.platform is None:
            return ''
