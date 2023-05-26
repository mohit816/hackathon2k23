from flask import Flask, request, jsonify, session
import jwt
import os
from werkzeug.utils import secure_filename
import csv
from Backend import Backend
from functools import wraps

app = Flask(__name__)
app.secret_key = '458cc0d8c5d6fb02175a21e3a58be785'  # Update with your secret key
backend = Backend()

# Mock database or backend for authentication
def authenticate(username, password):
    # Your authentication logic here
    # Return the user's role if authenticated, otherwise None
    if username == 'studio' and password == 'password':
        return 'studio'
    elif username == 'concept' and password == 'password':
        return 'concept'
    else:
        return None


# Decorator to check if the token is valid and extract the user details
def authenticate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Authorization token is missing'}), 401

        try:
            # Verify and decode the token
            payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            username = payload['username']
            role = payload['role']

            # Add the user details to the kwargs
            kwargs['username'] = username
            kwargs['role'] = role

            # Call the decorated function
            return func(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401

        except (jwt.InvalidTokenError, KeyError):
            return jsonify({'message': 'Invalid token'}), 401

    return wrapper



def allowed_file(filename):
    # Add your file extension validation logic here
    allowed_extensions = {'csv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/upload', methods=['POST'])
@authenticate_token
def upload_csv(username,role):
    if role != 'studio':  # Check the role
        return jsonify({'message': 'Unauthorized'}), 401

    if 'csv-file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['csv-file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        concept = request.form.get('concept')
        product_origin = request.form.get('product_origin')

        try:
            # Specify the encoding when opening the file
            with open(file_path, 'r', encoding='utf-8') as f:
                # Process the file data
                # ...

                return jsonify({'message': 'File uploaded and processed successfully'}), 200

        except UnicodeDecodeError:
            return jsonify({'message': 'Invalid file encoding'}), 400

    else:
        return jsonify({'message': 'Invalid file format'}), 400




@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API'}), 200


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.json  # Get the JSON data from the request body
        username = data.get('username')
        password = data.get('password')
        print(f"Received login request: username={username}, password={password}")

        role = authenticate(username, password)
        print(f"Authentication result: role={role}")

        if role:
            # Generate JWT token
            token = jwt.encode({'username': username, 'role': role}, app.secret_key, algorithm='HS256')

            return jsonify({'message': 'Login successful', 'role': role, 'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'message': 'Invalid request method'}), 400


@app.route('/dashboard', methods=['GET'])
@authenticate_token
def dashboard(**kwargs):
    role = kwargs.get('role')

    if role == 'studio':
        concept_values = ['MAX', 'SHOEMART', 'STYLI']
        product_origin_values = ['SAMPLE', 'SUPPLIER', 'WAREHOUSE']
        return jsonify({'message': 'Welcome to the studio dashboard', 'role': role,
                        'concept_values': concept_values, 'product_origin_values': product_origin_values}), 200
    elif role == 'concept':
        return jsonify({'message': 'Welcome to the concept dashboard', 'role': role}), 200
    else:
        return jsonify({'message': 'Unknown role'}), 401


if __name__ == '__main__':
    app.run(debug=True)
