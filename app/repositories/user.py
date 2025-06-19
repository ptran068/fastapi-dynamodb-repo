# app/repositories/user_repository.py

import boto3
from typing import Dict, Any, Optional, List
from app.database.base_repository import BaseRepository
from app.core.config import settings
from app.models.user import User
from botocore.exceptions import ClientError
from datetime import datetime
import uuid

class UserRepository(BaseRepository):
    def __init__(self, db_client: Any):
        super().__init__(f"{settings.DYNAMODB_TABLE_PREFIX}Users", db_client)
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_table(db_client)
            else:
                raise e

    def _create_table(self, db_client: Any):
        table_name = self.table.name

        db_client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'company', 'AttributeType': 'S'},
                {'AttributeName': 'jobTitle', 'AttributeType': 'S'},
                {'AttributeName': 'city', 'AttributeType': 'S'},
                {'AttributeName': 'state', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'CompanyIndex',
                    'KeySchema': [{'AttributeName': 'company', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'JobTitleIndex',
                    'KeySchema': [{'AttributeName': 'jobTitle', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'CityStateIndex',
                    'KeySchema': [
                        {'AttributeName': 'city', 'KeyType': 'HASH'},
                        {'AttributeName': 'state', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                 {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ]
        )
        self.table = db_client.Table(table_name)
        self.table.wait_until_exists()

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(Key={'id': user_id})
        return response.get('Item')

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        response = self.table.query(
            IndexName='EmailIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )
        items = response.get('Items', [])
        return items[0] if items else None

    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user = User(**user_data)
        item_to_put = user.model_dump()
        self.table.put_item(Item=item_to_put)
        return item_to_put

    async def update(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates['updatedAt'] = datetime.utcnow().isoformat()
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expression_attribute_names = {f"#{k}": k for k in updates.keys()}
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}

        try:
            response = self.table.update_item(
                Key={'id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            return None

    async def delete(self, user_id: str) -> bool:
        try:
            self.table.delete_item(Key={'id': user_id})
            return True
        except ClientError as e:
            return False

    async def query(self, **kwargs) -> List[Dict[str, Any]]:
        response = self.table.scan()
        return response.get('Items', [])