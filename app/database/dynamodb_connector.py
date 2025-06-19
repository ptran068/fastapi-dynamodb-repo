# app/database/dynamodb_connector.py
import boto3
from app.core.config import settings

class DynamoDBConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamoDBConnector, cls).__new__(cls)
            cls._instance.db = boto3.resource(
                'dynamodb',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME
            )
        return cls._instance

    def get_db(self):
        return self.db

dynamodb_connector = DynamoDBConnector()

def get_db_client():
    return dynamodb_connector.get_db()