"""
base.py — Generic CRUD base class for MongoDB (ODMantic).

Why a base class?
  Every resource (User, Product, Order …) needs the same four operations:
  create, read, update, delete. Instead of writing them per model, we write
  them ONCE here using Python generics and inherit in every CRUD file.

  This is the DRY (Don't Repeat Yourself) principle in action.

Usage:
    class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
        def __init__(self):
            super().__init__(model=User)
"""

from typing import Any, Generic, TypeVar

from bson import ObjectId
from odmantic import AIOEngine
from pydantic import BaseModel

from core import logger
from core.database.base_class import Base
from core.database.database import get_engine

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logging = logger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        Args:
            model: The ODMantic model class this CRUD operates on.

        The shared ODMantic engine is imported here once and reused by all
        CRUD methods, so the router and controller layers do not need to
        receive a database parameter.
        """
        self.model = model
        self.engine: AIOEngine = get_engine()

    async def get(self, id: Any) -> ModelType | None:
        """
        Fetch a single document by its MongoDB ObjectId.

        Args:
            id: ObjectId or 24-char hex string

        Returns:
            ModelType instance or None if not found
        """
        try:
            if isinstance(id, str) and len(id) == 24:
                id = ObjectId(id)
            return await self.engine.find_one(self.model, self.model.id == id)
        except Exception as error:
            logging.error(f"CRUDBase.get error: {error}")
            raise

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Fetch a paginated list of all documents in the collection.

        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum documents to return
        """
        try:
            return await self.engine.find(self.model, skip=skip, limit=limit)
        except Exception as error:
            logging.error(f"CRUDBase.get_all error: {error}")
            raise

    async def create(self, *, obj_in: CreateSchemaType | dict) -> ModelType:
        """
        Insert a new document into the collection.

        Args:
            obj_in: Pydantic schema or plain dict with the document data

        Returns:
            The saved ModelType instance (with _id populated)
        """
        try:
            if isinstance(obj_in, BaseModel):
                data = obj_in.model_dump()
            else:
                data = dict(obj_in)
            db_obj = self.model(**data)
            return await self.engine.save(db_obj)
        except Exception as error:
            logging.error(f"CRUDBase.create error: {error}")
            raise

    async def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict
    ) -> ModelType:
        """
        Update an existing document with partial data.

        Args:
            db_obj: The existing ODMantic model instance fetched from DB
            obj_in: Pydantic schema or dict containing only the fields to update

        Returns:
            Updated ModelType instance
        """
        try:
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            return await self.engine.save(db_obj)
        except Exception as error:
            logging.error(f"CRUDBase.update error: {error}")
            raise

    async def delete(self, *, id: Any) -> bool:
        """
        Delete a document by ID.

        Returns:
            True if deleted, False if not found
        """
        try:
            obj = await self.get(id=id)
            if obj:
                await self.engine.delete(obj)
                return True
            return False
        except Exception as error:
            logging.error(f"CRUDBase.delete error: {error}")
            raise
