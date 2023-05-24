from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
socketio = SocketIO(app)

# Configure the secret key
app.config['SECRET_KEY'] = '77c9232f44e495f0c83c5f994ed70087'

# File path for the tracker data CSV file
csv_file_path = 'tracker_data.csv'

# Initialize an empty DataFrame for tracker data
tracker_data = pd.DataFrame()

# User class for authentication
class User(UserMixin):
    def __init__(self, username, password, role):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

# User credentials dictionary
users = {
    'studio_user': User('studio_user', 'studio_password', 'studio'),
    'cc_user': User('cc_user', 'cc_password', 'cc'),
    'concept_user': User('concept_user', 'concept_password', 'concept'),
    'general_user': User('general_user', 'general_password', 'general')
}

# Initialize the login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return users.get(username)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Index route
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Upload route
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(os.getcwd(), filename)  # Set file path to current working directory
            file.save(file_path)
            load_tracker_data(file_path)  # Load the uploaded file into tracker data
            return 'File uploaded successfully!'
    return 'Invalid request method or no file provided.'

# Add data route
@app.route('/add_data', methods=['POST'])
@login_required
def add_data():
    if request.method == 'POST':
        new_data = request.form.to_dict()
        add_tracker_data(new_data)  # Add new data to the tracker data
        save_tracker_data()  # Save the updated data to the CSV file
        return 'Data added successfully!'
    return 'Invalid request method.'

# Search route
@app.route('/search', methods=['POST'])
@login_required
def search():
    if request.method == 'POST':
        concept = request.form.get('concept')
        sku = request.form.get('sku')
        status = request.form.get('status')
        result = search_tracker_data(concept, sku, status)  # Search for data in the tracker data
        return render_template('search_result.html', result=result)
    return 'Invalid request method.'

# Load tracker data from a file
def load_tracker_data(file_path):
    global tracker_data
    if os.path.isfile(csv_file_path):
        tracker_data = pd.read_csv(csv_file_path)
    else:
        tracker_data = pd.DataFrame(columns=['Concept', 'SKU', 'Shoot Date', 'Photographer', 'Stylist', 'Offline-CC', 'Comments', 'Status'])
    new_data = pd.read_csv(file_path)
    tracker_data = pd.concat([tracker_data, new_data], ignore_index=True)

# Add new data to the tracker data
def add_tracker_data(new_data):
    global tracker_data
    if isinstance(new_data, dict):
        new_data = pd.DataFrame(new_data, index=[0])
    tracker_data = pd.concat([tracker_data, new_data], ignore_index=True)
    tracker_data = tracker_data.drop_duplicates()

# Save the tracker data to a CSV file
def save_tracker_data():
    global tracker_data, csv_file_path
    tracker_data.to_csv(csv_file_path, index=False)

# Search for data in the tracker data
def search_tracker_data(concept, sku, status):
    global tracker_data
    result = tracker_data
    if concept:
        result = result[result['Concept'] == concept]
    if sku:
        result = result[result['SKU'] == sku]
    if status:
        result = result[result['Status'] == status]
    return result.to_dict('records')

# Role-based access decorator
def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role == role:
                return func(*args, **kwargs)
            else:
                abort(403)  # Access denied
        return wrapper
    return decorator

# Studio dashboard route (accessible only to users with 'studio' role)
@app.route('/studio_dashboard')
@login_required
@role_required('studio')
def studio_dashboard():
    # ...
    pass

# CC dashboard route (accessible only to users with 'cc' role)
@app.route('/cc_dashboard')
@login_required
@role_required('cc')
def cc_dashboard():
    # ...
    pass

# Concept dashboard route (accessible only to users with 'concept' role)
@app.route('/concept_dashboard')
@login_required
@role_required('concept')
def concept_dashboard():
    # ...
    pass

# General dashboard route (accessible only to users with 'general' role)
@app.route('/general_dashboard')
@login_required
@role_required('general')
def general_dashboard():
    # ...
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
