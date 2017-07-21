from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://blogz:password@localhost:8889/blogz')
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


# User Class

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username

# Blog Class

class Blog(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(200))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, title, body, owner):
		self.title = title
		self.body = body
		self.owner = owner

# Login / Register Controllers

@app.route('/')
def index():
	
	return render_template('index.html')

# Existing Session Handler
@app.before_request
def before_request():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        redirect('/login')


# Login 
@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user = User.query.filter_by(email=email).first()

		if user and user.password == password:
			session['email'] = email
			return render_template('home.html', username=user.username)
		else:
			return render_template('login.html', login_error='Username or password is incorrect', 
				email=email)

	return render_template('login.html')

# Register
@app.route('/register', methods=['POST', 'GET'])
def register():
	print('received request at register')
	if request.method == 'GET':
		return render_template('register.html')

	username = request.form['username']
	email = request.form['email']
	password = request.form['password']
	verify = request.form['verify']

	email_error = ''
	username_error = ''
	password_error = ''

	if not username:
		username_error = 'Not a valid username.'

	if not password:
		password_error = 'Must enter a password.'

	if not verify:
		password_error = 'Must verify password.'

	if len(password) < 3 or len(password) > 20:
		password_error = 'Password must be between 3-20 characters.'

	if ' ' in password:
		password_error = 'Password cannot contain spaces.'

	if not password == verify:
		password_error = 'Passwords do not match.'

	if '@' not in email and '.' not in email:
		email_error = 'Not a vaild email'

	if len(email) < 3 or len(email) > 20:
		email_error = 'Email must be between 3-20 characters.'

	if ' ' in email:
		email_error = 'Email cannot contain spaces.'

	if not email_error and not username_error and not password_error:

		existing_user = User.query.filter_by(email=email).first()
		existing_username = User.query.filter_by(username=username).first()

		if not existing_user and not existing_username:
			new_user = User(email, password, username)
			db.session.add(new_user)
			db.session.commit()
			session['email'] = email
			return redirect('/home')

		else:
			return render_template('register.html', username_error='User already exists.')
	else:

		return render_template(
		'register.html',
		email=email,
		username=username, 
		email_error=email_error,
		username_error=username_error,
		password_error=password_error,
	)

# Home Page
@app.route("/home", methods=['POST', 'GET'])
def home():
	email = session['email']
	username = User.query.filter_by(email=email).first().username

	owner = User.query.filter_by(email=session['email']).first()

	blogs = Blog.query.filter_by(owner=owner).all()

	return render_template('home.html', username=username, blogs=blogs)

# Logout
@app.route('/logout')
def logout():
	del session['email']
	return render_template('login.html')

# Blog Controller

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
	if request.method == 'POST':
		title = request.form.get('blogtitle')
		body = request.form.get('blogbody')

		owner = User.query.filter_by(email=session['email']).first()

		new_blog = Blog(title, body, owner)
		db.session.add(new_blog)
		db.session.commit()

		return render_template('post.html', title=title, body=body, owner=owner)

	return render_template('newpost.html')

# Individual Post
@app.route('/post/<id>')
def post(id):

	blog = Blog.query.filter_by(id=id).first()
	owner = blog.owner

	return render_template('post.html', title=blog.title, body=blog.body, owner=owner)

# Profile View
@app.route('/profile/<id>')
def profile(id):

	owner = User.query.filter_by(id=id).first()
	blogs = Blog.query.filter_by(owner=owner).all()

	return render_template('profile.html', username=owner.username, blogs=blogs)

# Users View
@app.route('/users')
def users():
	owners = User.query.all()

	return render_template('users.html', owners=owners)

# Viewing All Blogs
@app.route('/allblogz')
def allblogz():
	blogs = Blog.query.all()
	owners = User.query.all()

	return render_template('allblogz.html', blogs=blogs, owners=owners)

if __name__ == '__main__':
	app.run()