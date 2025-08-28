"""
Schema Unit Tests

Test Pydantic schemas validation logic
"""

import pytest
from pydantic import ValidationError
from andamios_api.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from andamios_api.schemas.item import ItemBase, ItemCreate, ItemUpdate, ItemResponse


class TestUserSchemas:
    
    def test_user_base_valid(self):
        """Test valid UserBase creation"""
        user = UserBase(
            email="test@example.com",
            name="John Doe"
        )
        assert user.email == "test@example.com"
        assert user.name == "John Doe"
    
    def test_user_base_name_validation(self):
        """Test UserBase name validation"""
        # Valid name
        user = UserBase(email="test@example.com", name="John Doe")
        assert user.name == "John Doe"
        
        # Name with whitespace gets trimmed
        user = UserBase(email="test@example.com", name="  John Doe  ")
        assert user.name == "John Doe"
        
        # Empty name should raise error
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", name="")
        assert "Name cannot be empty" in str(exc_info.value)
        
        # Whitespace-only name should raise error
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", name="   ")
        assert "Name cannot be empty" in str(exc_info.value)
    
    def test_user_base_email_validation(self):
        """Test UserBase email validation"""
        # Valid email
        user = UserBase(email="test@example.com", name="John Doe")
        assert user.email == "test@example.com"
        
        # Invalid email format should raise error
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="not-an-email", name="John Doe")
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_valid(self):
        """Test valid UserCreate"""
        user = UserCreate(
            email="test@example.com",
            name="John Doe",
            password="validpassword123"
        )
        assert user.email == "test@example.com"
        assert user.name == "John Doe"
        assert user.password == "validpassword123"
    
    def test_user_create_password_validation(self):
        """Test UserCreate password validation"""
        # Valid password
        user = UserCreate(
            email="test@example.com",
            name="John Doe",
            password="validpassword123"
        )
        assert user.password == "validpassword123"
        
        # Password too short should raise error
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                name="John Doe",
                password="short"
            )
        assert "at least 8 characters" in str(exc_info.value)
    
    def test_user_update_optional_fields(self):
        """Test UserUpdate with optional fields"""
        # Empty update
        user = UserUpdate()
        assert user.email is None
        assert user.name is None
        
        # Partial update
        user = UserUpdate(name="New Name")
        assert user.name == "New Name"
        assert user.email is None
        
        # Full update
        user = UserUpdate(email="new@example.com", name="New Name")
        assert user.email == "new@example.com"
        assert user.name == "New Name"
    
    def test_user_update_name_validation(self):
        """Test UserUpdate name validation"""
        # Valid name gets trimmed
        user = UserUpdate(name="  Valid Name  ")
        assert user.name == "Valid Name"
        
        # Empty name should raise error
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(name="")
        assert "Name cannot be empty" in str(exc_info.value)


class TestItemSchemas:
    
    def test_item_base_valid(self):
        """Test valid ItemBase creation"""
        item = ItemBase(
            name="Test Item",
            description="Test description"
        )
        assert item.name == "Test Item"
        assert item.description == "Test description"
    
    def test_item_base_name_validation(self):
        """Test ItemBase name validation"""
        # Valid name
        item = ItemBase(name="Test Item")
        assert item.name == "Test Item"
        
        # Name with whitespace gets trimmed
        item = ItemBase(name="  Test Item  ")
        assert item.name == "Test Item"
        
        # Empty name should raise error
        with pytest.raises(ValidationError) as exc_info:
            ItemBase(name="")
        assert "Name is required" in str(exc_info.value)
        
        # Whitespace-only name should raise error
        with pytest.raises(ValidationError) as exc_info:
            ItemBase(name="   ")
        assert "Name is required" in str(exc_info.value)
    
    def test_item_base_description_validation(self):
        """Test ItemBase description validation"""
        # Valid description
        item = ItemBase(name="Test", description="Valid description")
        assert item.description == "Valid description"
        
        # None description
        item = ItemBase(name="Test", description=None)
        assert item.description is None
        
        # Empty description gets converted to None
        item = ItemBase(name="Test", description="")
        assert item.description is None
        
        # Whitespace-only description gets converted to None
        item = ItemBase(name="Test", description="   ")
        assert item.description is None
        
        # Description with content gets trimmed
        item = ItemBase(name="Test", description="  Valid description  ")
        assert item.description == "Valid description"
    
    def test_item_create_inheritance(self):
        """Test ItemCreate inherits from ItemBase"""
        item = ItemCreate(
            name="Test Item",
            description="Test description"
        )
        assert item.name == "Test Item"
        assert item.description == "Test description"
        
        # Should have same validation as ItemBase
        with pytest.raises(ValidationError):
            ItemCreate(name="")
    
    def test_item_update_optional_fields(self):
        """Test ItemUpdate with optional fields"""
        # Empty update
        item = ItemUpdate()
        assert item.name is None
        assert item.description is None
        
        # Partial update
        item = ItemUpdate(name="New Name")
        assert item.name == "New Name"
        assert item.description is None
        
        # Full update
        item = ItemUpdate(name="New Name", description="New description")
        assert item.name == "New Name"
        assert item.description == "New description"
    
    def test_item_update_validation(self):
        """Test ItemUpdate field validation"""
        # Valid name gets trimmed
        item = ItemUpdate(name="  Valid Name  ")
        assert item.name == "Valid Name"
        
        # Empty name should raise error
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(name="")
        assert "Name cannot be empty" in str(exc_info.value)
        
        # Empty description gets converted to None
        item = ItemUpdate(description="")
        assert item.description is None
    
    def test_item_response_config(self):
        """Test ItemResponse configuration"""
        # Create from dict (simulates ORM object)
        data = {
            "id": 1,
            "name": "Test Item",
            "description": "Test description"
        }
        
        # Should work with from_attributes=True
        item = ItemResponse(**data)
        assert item.id == 1
        assert item.name == "Test Item"
        assert item.description == "Test description"


class TestSchemaIntegration:
    
    def test_schema_field_constraints(self):
        """Test Pydantic Field constraints"""
        
        # Test name length constraints
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="A",  # Too short (min_length=2)
                password="validpassword"
            )
        
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="A" * 51,  # Too long (max_length=50)
                password="validpassword"
            )
        
        # Test item name length constraints
        with pytest.raises(ValidationError):
            ItemCreate(name="A" * 201)  # Too long (max_length=200)
        
        # Test item description length constraints
        with pytest.raises(ValidationError):
            ItemCreate(
                name="Valid Name",
                description="A" * 501  # Too long (max_length=500)
            )