"""
Item model using andamios-orm base Model class

Rules:
- Inherits from andamios-orm Model for CRUD classmethods
- Defines SQLAlchemy columns for Item table
- No business logic here - just data structure
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from andamios_orm.models.base import Model
from .user import APIBase

class Item(Model, APIBase):
    """Item model with andamios-orm integration"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)  # Removed autoincrement for DuckDB compatibility
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @classmethod
    def _validate_create(cls, **kwargs):
        """Validate item creation data"""
        if not kwargs.get('name'):
            raise ValueError("Name is required")
    
    @classmethod
    def _validate_update(cls, **kwargs):
        """Validate item update data"""
        if 'name' in kwargs and not kwargs['name']:
            raise ValueError("Name cannot be empty")