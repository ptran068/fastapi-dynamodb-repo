# app/database/base_repository.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import uuid

class BaseRepository(ABC):
    def __init__(self, table_name: str, db_client: Any):
        self.table = db_client.Table(table_name)

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        pass

    @abstractmethod
    async def query(self, **kwargs) -> List[Dict[str, Any]]:
        pass