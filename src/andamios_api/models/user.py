"""
User model using andamios-orm base Model class

Rules:
- Inherits from andamios-orm Model for CRUD classmethods
- Defines SQLAlchemy columns for User table
- No business logic here - just data structure
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from andamios_orm.models.base import Model
from sqlalchemy.ext.declarative import declarative_base

# Create a separate Base for our API models to avoid conflicts
APIBase = declarative_base()

class User(Model, APIBase):
    """User model with andamios-orm integration"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)  # Removed autoincrement for DuckDB compatibility
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @classmethod
    def _validate_create(cls, **kwargs):
        """Validate user creation data"""
        if not kwargs.get('email'):
            raise ValueError("Email is required")
        if not kwargs.get('name'):
            raise ValueError("Name is required")
        if not kwargs.get('password_hash'):
            raise ValueError("Password hash is required")
    
    @classmethod
    def _validate_update(cls, **kwargs):
        """Validate user update data"""
        if 'email' in kwargs and not kwargs['email']:
            raise ValueError("Email cannot be empty")
        if 'name' in kwargs and not kwargs['name']:
            raise ValueError("Name cannot be empty")