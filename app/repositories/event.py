# app/repositories/event_repository.py
import boto3
from typing import Dict, Any, Optional, List
from app.database.base_repository import BaseRepository
from app.core.config import settings
from app.models.event import Event
from botocore.exceptions import ClientError
from datetime import datetime
import uuid


class EventRepository(BaseRepository):
    def __init__(self, db_client: Any):
        super().__init__(f"{settings.DYNAMODB_TABLE_PREFIX}Events", db_client)
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
                {'AttributeName': 'slug', 'AttributeType': 'S'},
                {'AttributeName': 'ownerId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'SlugIndex',
                    'KeySchema': [{'AttributeName': 'slug', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'OwnerIdIndex',
                    'KeySchema': [{'AttributeName': 'ownerId', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ]
        )

        self.table = db_client.Table(table_name)
        self.table.wait_until_exists()

    async def get_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(Key={'id': event_id})
        return response.get('Item')

    async def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        response = self.table.query(
            IndexName='SlugIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('slug').eq(slug)
        )
        items = response.get('Items', [])
        return items[0] if items else None

    async def create(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event = Event(**event_data)

        item_to_put = event.model_dump()
        item_to_put['startAt'] = item_to_put['startAt'].isoformat()
        item_to_put['endAt'] = item_to_put['endAt'].isoformat()

        self.table.put_item(Item=item_to_put)
        return item_to_put  # Return the standardized dict

    async def update(self, event_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates['updatedAt'] = datetime.utcnow().isoformat()

        if 'startAt' in updates and isinstance(updates['startAt'], datetime):
            updates['startAt'] = updates['startAt'].isoformat()
        if 'endAt' in updates and isinstance(updates['endAt'], datetime):
            updates['endAt'] = updates['endAt'].isoformat()

        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expression_attribute_names = {f"#{k}": k for k in updates.keys()}
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}

        try:
            response = self.table.update_item(
                Key={'id': event_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            return None

    async def delete(self, event_id: str) -> bool:
        try:
            self.table.delete_item(Key={'id': event_id})
            return True
        except ClientError as e:
            return False

    async def query(self, **kwargs) -> List[Dict[str, Any]]:
        response = self.table.scan()
        return response.get('Items', [])