from flask import Flask, render_template, request
import pandas as pd
import os
from flask_socketio import SocketIO

from werkzeug.utils import secure_filename


app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = '77c9232f44e495f0c83c5f994ed70087'

# File path for the tracker data CSV file
csv_file_path = 'tracker_data.csv'

# Initialize an empty DataFrame for tracker data
tracker_data = pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')


# ...

@app.route('/upload', methods=['POST'])
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


@app.route('/add_data', methods=['POST'])
def add_data():
    if request.method == 'POST':
        new_data = request.form.to_dict()
        add_tracker_data(new_data)  # Add new data to the tracker data
        save_tracker_data()  # Save the updated data to the CSV file
        return 'Data added successfully!'
    return 'Invalid request method.'

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        concept = request.form.get('concept')
        sku = request.form.get('sku')
        status = request.form.get('status')
        result = search_tracker_data(concept, sku, status)  # Search for data in the tracker data
        return render_template('search_result.html', result=result)
    return 'Invalid request method.'

def load_tracker_data(file_path):
    global tracker_data
    if os.path.isfile(csv_file_path):
        tracker_data = pd.read_csv(csv_file_path)
    else:
        tracker_data = pd.DataFrame(columns=['Concept', 'SKU', 'Shoot Date', 'Photographer', 'Stylist', 'Offline-CC', 'Comments', 'Status'])
    new_data = pd.read_csv(file_path)
    tracker_data = pd.concat([tracker_data, new_data], ignore_index=True)

def add_tracker_data(new_data):
    global tracker_data
    if isinstance(new_data, dict):
        new_data = pd.DataFrame(new_data, index=[0])
    tracker_data = pd.concat([tracker_data, new_data], ignore_index=True)
    tracker_data = tracker_data.drop_duplicates()

def save_tracker_data():
    global tracker_data, csv_file_path
    tracker_data.to_csv(csv_file_path, index=False)

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

if __name__ == '__main__':
    socketio.run(app, debug=True)
