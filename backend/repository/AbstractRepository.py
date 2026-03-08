from typing import Optional
from backend.domain.entities.Entity import Entity

# TODO: Repository package logging!!!!!!
class AbstractRepository:
    """
    Abstract Repository Class

    Contains the following basic CRUD operations:
     - create: creates a new entity
     - get_by_id: gets a single entity by its id
     - find_by_name_paged: finds entities by their name (str attribute)
     - update: updates an entity
     - delete: deletes an entity
    """
    def create(self, obj: Entity) -> Optional[Entity]: raise NotImplementedError
    def get_by_id(self, obj_id: int) -> Optional[Entity]: raise NotImplementedError
    def find_by_name_paged(self, name: str, limit: int, offset: int) -> list[Entity]: raise NotImplementedError
    def update(self, obj: Entity) -> Optional[Entity]: raise NotImplementedError
    def delete(self, obj_id: int) -> Optional[Entity]: raise NotImplementedError