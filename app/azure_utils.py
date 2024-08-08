from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import requests
from datetime import datetime, timedelta

def upload_to_blob(container_name, blob_name, file_content, connection_string):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(file_content, overwrite=True)
    return blob_client.url

def trigger_azure_function(function_url, values):
    json_request = {
        "values": values
    }
    response = requests.post(function_url, json=json_request)
    return response

def get_blob_url_with_sas(container_name, blob_name, connection_string):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return blob_url
