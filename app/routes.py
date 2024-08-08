from flask import Blueprint, render_template, request, jsonify, url_for
from app.azure_utils import upload_to_blob, trigger_azure_function, get_blob_url_with_sas
from config import Config
import uuid
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # List sample files from the 'sample_forms' directory
    sample_files = os.listdir('sample_forms')
    return render_template('index.html', sample_files=sample_files)

@main.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files[]')
    sample_files = request.form.getlist('sample_files[]')

    if not files and not sample_files:
        return jsonify({"error": "No files selected"}), 400

    try:
        file_urls = []

        # Process uploaded files (drag-and-drop or file input)
        for file in files:
            if file.filename == '':
                continue
            blob_name = f"{uuid.uuid4()}-{file.filename}"
            file_content = file.read()
            upload_to_blob(Config.INPUT_CONTAINER_NAME, blob_name, file_content, Config.AZURE_STORAGE_CONNECTION_STRING)
            blob_url = f"https://{Config.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{Config.INPUT_CONTAINER_NAME}/{blob_name}"
            file_urls.append(blob_url)

        # Process selected sample files
        for file_name in sample_files:
            # Read the sample file from 'sample_forms' directory
            sample_file_path = os.path.join('sample_forms', file_name)
            if not os.path.exists(sample_file_path):
                return jsonify({"error": f"Sample file '{file_name}' not found"}), 404
            
            with open(sample_file_path, 'rb') as sample_file:
                blob_name = f"{uuid.uuid4()}-{file_name}"
                file_content = sample_file.read()
                upload_to_blob(Config.INPUT_CONTAINER_NAME, blob_name, file_content, Config.AZURE_STORAGE_CONNECTION_STRING)
                blob_url = f"https://{Config.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{Config.INPUT_CONTAINER_NAME}/{blob_name}"
                file_urls.append(blob_url)
        
        static_sas_token = "?st=sasTokenThatWillBeGeneratedByCognitiveSearch"
        values = [{"recordId": f"record{i+1}", "data": {"formUrl": url, "formSasToken": static_sas_token}} for i, url in enumerate(file_urls)]

        response = trigger_azure_function(Config.AZURE_FUNCTION_URL, values)
        
        if response.status_code != 200:
            return jsonify({"error": f"Azure Function error: {response.text}"}), 500

        return jsonify({"message": "Processing", "downloadUrl": url_for('main.download')}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@main.route('/download', methods=['GET'])
def download():
    try:
        blob_name = "extracted_data.xlsx"
        blob_url = get_blob_url_with_sas(Config.OUTPUT_CONTAINER_NAME, blob_name, Config.AZURE_STORAGE_CONNECTION_STRING)

        return jsonify({"file_url": blob_url}), 200
    except Exception as e:
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500
