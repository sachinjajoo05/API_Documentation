import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5")
    AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    @staticmethod
    def validate():
        """Ensure critical configurations are present"""
        if not Config.AZURE_ENDPOINT or not Config.AZURE_API_KEY:
            raise ValueError("Missing Azure OpenAI credentials in .env file")