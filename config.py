import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

load_dotenv()

class Config:
    AZURE_FUNCTION_URL = None
    INPUT_CONTAINER_NAME = os.getenv('INPUT_CONTAINER_NAME')
    OUTPUT_CONTAINER_NAME = os.getenv('OUTPUT_CONTAINER_NAME')
    AZURE_STORAGE_CONNECTION_STRING = None
    AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')

    @staticmethod
    def load_secrets():
        try:
            # Get Configuration Settings from environment variables
            key_vault_name = os.getenv('KEY_VAULT')
            app_tenant = os.getenv('TENANT_ID')
            app_id = os.getenv('APP_ID')
            app_password = os.getenv('APP_PASSWORD')

            # Ensure required environment variables are set
            if not all([key_vault_name, app_tenant, app_id, app_password]):
                raise ValueError("Missing one or more required environment variables.")

            # Construct the Key Vault URI
            key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

            # Create a credential using the service principal
            credential = ClientSecretCredential(app_tenant, app_id, app_password)

            # Create a SecretClient to access the Key Vault
            keyvault_client = SecretClient(vault_url=key_vault_uri, credential=credential)

            # Get the Azure Storage Connection String from Key Vault
            storage_secret = keyvault_client.get_secret("storage-docfunctionapp11-string")
            Config.AZURE_STORAGE_CONNECTION_STRING = storage_secret.value

            # Get the Azure Function URL from Key Vault
            function_url_secret = keyvault_client.get_secret("docfunctionapp11-Analyze-Form-URL")
            Config.AZURE_FUNCTION_URL = function_url_secret.value

        except Exception as e:
            raise Exception(f"Failed to load secrets from Azure Key Vault: {str(e)}")

# Load the secrets when the module is imported
Config.load_secrets()
