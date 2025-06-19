import boto3
import boto3.dynamodb.conditions as KeyC
from typing import Dict, Any, Optional, List
from app.database.base_repository import BaseRepository
from app.core.config import settings
from botocore.exceptions import ClientError
from datetime import datetime
import uuid

class UserEventRepository(BaseRepository):
    def __init__(self, db_client: Any):
        super().__init__(f"{settings.DYNAMODB_TABLE_PREFIX}UserEvents", db_client)
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_table(db_client)
            else:
                raise e

    def _create_table(self, db_client: Any):
        """
        Creates the UserEvents DynamoDB table with userId as HASH and eventId as RANGE key.
        Also creates a GSI on EventIdIndex for reverse lookups.
        """
        table_name = self.table.name

        db_client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'},
                {'AttributeName': 'eventId', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                # Only define attributes used in KeySchema (main table or GSI)
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'eventId', 'AttributeType': 'S'}
                # REMOVED: {'AttributeName': 'role', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EventIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'eventId', 'KeyType': 'HASH'},
                        {'AttributeName': 'userId', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ]
        )

        self.table = db_client.Table(table_name)
        self.table.wait_until_exists()
    # --- Implementations for Abstract Methods from BaseRepository ---
    async def create(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements the abstract 'create' method.
        Expects item_data to contain 'userId', 'eventId', and 'role'.
        """
        user_id = item_data.get('userId')
        event_id = item_data.get('eventId')
        role = item_data.get('role')

        if not all([user_id, event_id, role]):
            raise ValueError("item_data must contain 'userId', 'eventId', and 'role' for UserEvent creation.")

        return await self.create_user_event(user_id, event_id, role)

    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Implements the abstract 'get_by_id' method.
        NOTE: UserEvent requires a composite key (userId, eventId).
        This method cannot uniquely identify a UserEvent with a single ID.
        Use get_user_event(userId, eventId) instead.
        """
        raise ValueError(
            "UserEventRepository requires a composite key (userId, eventId) for identification. "
            "Use 'get_user_event(user_id, event_id)' instead of 'get_by_id(item_id)'."
        )

    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Implements the abstract 'update' method.
        NOTE: UserEvent requires a composite key (userId, eventId) for updates.
        This method cannot uniquely identify a UserEvent with a single ID.
        Use update_user_event(userId, eventId, updates) instead.
        """
        raise ValueError(
            "UserEventRepository requires a composite key (userId, eventId) for updates. "
            "Use 'update_user_event(user_id, event_id, updates)' instead of 'update(item_id, updates)'."
        )

    async def delete(self, item_id: str) -> bool:
        """
        Implements the abstract 'delete' method.
        NOTE: UserEvent requires a composite key (userId, eventId) for deletion.
        This method cannot uniquely identify a UserEvent with a single ID.
        Use delete_user_event(userId, eventId) instead.
        """
        raise ValueError(
            "UserEventRepository requires a composite key (userId, eventId) for deletion. "
            "Use 'delete_user_event(user_id, event_id)' instead of 'delete(item_id)'."
        )
    # --- End of Abstract Method Implementations ---


    # --- Existing Specific Methods for UserEvent ---
    async def create_user_event(self, user_id: str, event_id: str, role: str) -> Dict[str, Any]:
        """
        Creates a new UserEvent entry with the composite key.
        """
        item = {
            'userId': user_id,
            'eventId': event_id,
            'role': role,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        self.table.put_item(Item=item)
        return item

    async def get_user_event(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific UserEvent entry by its composite primary key.
        """
        response = self.table.get_item(Key={'userId': user_id, 'eventId': event_id})
        return response.get('Item')

    async def get_events_for_user(self, user_id: str, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves all events a user is involved in, optionally filtered by role.
        Uses the main table's primary key (userId).
        """
        query_params = {
            'KeyConditionExpression': KeyC.Key('userId').eq(user_id)
        }
        if role:
            query_params['FilterExpression'] = KeyC.Key('role').eq(role)

        response = self.table.query(**query_params)
        return response.get('Items', [])

    async def get_users_for_event(self, event_id: str, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves all users involved in a specific event, optionally filtered by role.
        Uses the 'EventIdIndex' GSI.
        """
        query_params = {
            'IndexName': 'EventIdIndex',
            'KeyConditionExpression': KeyC.Key('eventId').eq(event_id)
        }
        if role:
            query_params['FilterExpression'] = KeyC.Key('role').eq(role)

        response = self.table.query(**query_params)
        return response.get('Items', [])

    async def update_user_event(self, user_id: str, event_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates an existing UserEvent entry using its composite primary key.
        """
        updates['updatedAt'] = datetime.utcnow().isoformat()
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expression_attribute_names = {f"#{k}": k for k in updates.keys()}
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}

        try:
            response = self.table.update_item(
                Key={'userId': user_id, 'eventId': event_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error updating UserEvent: {e}")
            return None

    async def delete_user_event(self, user_id: str, event_id: str) -> bool:
        """
        Deletes a UserEvent entry using its composite primary key.
        """
        try:
            self.table.delete_item(Key={'userId': user_id, 'eventId': event_id})
            return True
        except ClientError as e:
            print(f"Error deleting UserEvent: {e}")
            return False

    async def query(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Performs a generic SCAN operation on the UserEvents table.
        """
        response = self.table.scan()
        return response.get('Items', [])