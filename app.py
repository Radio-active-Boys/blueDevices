import os
from flask import Flask, render_template, jsonify, send_file, send_from_directory
from pymongo import MongoClient
import csv
from io import BytesIO, StringIO
from dotenv import load_dotenv
import json


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB setup
# Access the environment variable
mongodb_uri = os.getenv("MONGODB_UR")
client = MongoClient(mongodb_uri)
db = client["bluetooth"]

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_collections')
def get_collections():
    collections = db.list_collection_names()
    return jsonify(collections)

@app.route('/get_data/<collection_name>')
def get_data(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)

@app.route('/download_csv/<collection_name>')
def download_csv(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))

    # Convert data to CSV format using StringIO
    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)

    # Create a response with CSV content
    response = send_file(
        BytesIO(csv_data.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{collection_name}.csv'
    )

    return response

@app.route('/download_json/<collection_name>')
def download_json(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))

    # Create a response with JSON content
    response = send_file(
        BytesIO(json.dumps(data, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{collection_name}.json'
    )

    return response


@app.route('/download_setup')
def download_setup():
    setup_file_path = os.path.join(app.root_path, 'file', 'setup.sh')
    return send_from_directory(app.root_path, 'file/setup.sh', as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

