import json
import pytest
from datetime import datetime, timezone
from typing import List, Optional, Set, Any, Dict
from pydantic import BaseModel, Field, field_validator
from pydantic_core import ValidationError

from redis_data_structures import ModelRegistry, RDSSerializer


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    
    @field_validator('latitude', 'longitude')
    def validate_coordinates(cls, v: float) -> float:
        if not isinstance(v, (int, float)):
            raise ValueError('Coordinate must be a number')
        return float(v)

class Address(BaseModel):
    street: str
    city: str
    country: str = Field(max_length=2)
    location: Optional[Location] = None
    
    @field_validator('country')
    def validate_country(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError('Country code must be exactly 2 characters')
        return v.upper()

class Contact(BaseModel):
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: Optional[str] = None
    preferred_method: str = Field(default="email")
    
    @field_validator('preferred_method')
    def validate_preferred_method(cls, v: str) -> str:
        if v not in ['email', 'phone']:
            raise ValueError('Preferred method must be either email or phone')
        return v

class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(gt=0, lt=150)
    addresses: List[Address]
    contact: Contact
    tags: Set[str] = set()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Test Cases
class TestModelRegistry:
    def setup_method(self):
        """Reset singleton instance before each test."""
        ModelRegistry._instance = None
        self.registry = ModelRegistry()

    def test_singleton_pattern(self):
        """Test singleton pattern implementation."""
        registry1 = ModelRegistry()
        registry2 = ModelRegistry()
        assert registry1 is registry2
        assert ModelRegistry() is registry1

    def test_register_simple_model(self):
        """Test registration of simple model."""
        self.registry.register_model(Location)
        assert "Location" in self.registry._models
        assert self.registry.get_model("Location") is Location
        
        # Test schema registration
        schema = self.registry.get_schema("Location")
        assert schema is not None
        assert "properties" in schema
        assert all(field in schema["properties"] for field in ["latitude", "longitude"])

    def test_register_nested_model(self):
        """Test registration of nested models."""
        self.registry.register_model(User)
        
        # Check all nested models are registered
        expected_models = {"User", "Address", "Contact", "Location"}
        registered_models = set(self.registry._models.keys())
        assert expected_models.issubset(registered_models)
        
        # Verify nested schemas
        for model_name in expected_models:
            assert self.registry.get_schema(model_name) is not None

    def test_registration_context(self):
        """Test registration context manager."""
        with self.registry.registration_context():
            self.registry.register_model(User)
        
        # Verify successful registration
        assert "User" in self.registry._models
        
        # Test cleanup on error
        initial_models = set(self.registry._models.keys())
        try:
            with self.registry.registration_context():
                self.registry.register_model(User)
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify no models were added during failed registration
        assert set(self.registry._models.keys()) == initial_models

    def test_get_nonexistent_model(self):
        """Test retrieval of non-existent model."""
        assert self.registry.get_model("NonexistentModel") is None
        assert self.registry.get_schema("NonexistentModel") is None

class TestRDSSerializer:
    def setup_method(self):
        """Reset for each test."""
        ModelRegistry._instance = None
        self.serializer = RDSSerializer()

    def test_serialize_simple_model(self):
        """Test serialization of simple model."""
        location = Location(latitude=40.7128, longitude=-74.0060)
        serialized = self.serializer.serialize(location)
        data = json.loads(serialized)
        
        assert data["_type"] == "Location"
        assert isinstance(data["value"], dict)
        assert data["value"]["latitude"] == 40.7128
        assert data["value"]["longitude"] == -74.0060
        assert "schema" in data
        assert data["schema"]["properties"]["latitude"]["type"] == "number"

    def test_serialize_complex_model(self):
        """Test serialization of complex nested model."""
        user = User(
            name="John Doe",
            age=30,
            addresses=[
                Address(
                    street="123 Main St",
                    city="NYC",
                    country="US",
                    location=Location(latitude=40.7128, longitude=-74.0060)
                )
            ],
            contact=Contact(
                email="john@example.com",
                phone="+1234567890",
                preferred_method="email"
            ),
            tags={"python", "developer"},
            metadata={"role": "admin"}
        )
        
        serialized = self.serializer.serialize(user)
        data = json.loads(serialized)
        
        assert data["_type"] == "User"
        assert "nested_types" in data
        assert all(model in data["nested_types"] for model in ["Address", "Contact", "Location"])
        assert isinstance(data["value"]["addresses"], list)
        assert isinstance(data["value"]["tags"], list)
        assert isinstance(data["value"]["metadata"], dict)

    def test_deserialize_with_validation(self):
        """Test deserialization with validation."""
        # Test valid data
        valid_user = User(
            name="John Doe",
            age=30,
            addresses=[Address(street="123 Main St", city="NYC", country="US")],
            contact=Contact(email="john@example.com")
        )
        serialized = self.serializer.serialize(valid_user)
        deserialized = self.serializer.deserialize(serialized)
        
        assert isinstance(deserialized, User)
        assert deserialized.name == valid_user.name
        
        # Test invalid age
        with pytest.raises(ValidationError):
            serialized_data = json.loads(serialized)
            serialized_data["value"]["age"] = 200  # Invalid age
            self.serializer.deserialize(json.dumps(serialized_data))
        
        # Test invalid email
        with pytest.raises(ValidationError):
            serialized_data = json.loads(serialized)
            serialized_data["value"]["contact"]["email"] = "invalid-email"
            self.serializer.deserialize(json.dumps(serialized_data))
        
        # Test invalid country code
        with pytest.raises(ValidationError):
            serialized_data = json.loads(serialized)
            serialized_data["value"]["addresses"][0]["country"] = "USA"  # Too long
            self.serializer.deserialize(json.dumps(serialized_data))

    def test_handle_invalid_data(self):
        """Test handling of invalid data."""
        invalid_cases = [
            '{"invalid": "data"}',
            'invalid json',
            '{"_type": "NonexistentModel", "value": {}}',
            '{"_type": "User", "value": {"invalid": "data"}}',
        ]
        
        for invalid_data in invalid_cases:
            with pytest.raises((ValueError, json.JSONDecodeError, ValidationError)):
                self.serializer.deserialize(invalid_data)

    def test_datetime_handling(self):
        """Test datetime field handling."""
        current_time = datetime.now(timezone.utc)
        user = User(
            name="John Doe",
            age=30,
            addresses=[Address(street="123 Main St", city="NYC", country="US")],
            contact=Contact(email="john@example.com"),
            created_at=current_time
        )
        
        serialized = self.serializer.serialize(user)
        deserialized = self.serializer.deserialize(serialized)
        
        assert isinstance(deserialized.created_at, datetime)
        assert deserialized.created_at.tzinfo is not None
        assert deserialized.created_at.replace(microsecond=0) == current_time.replace(microsecond=0)

    def test_collection_handling(self):
        """Test handling of collections (List, Set, Dict)."""
        user = User(
            name="John Doe",
            age=30,
            addresses=[
                Address(street="123 Main St", city="NYC", country="US"),
                Address(street="456 Park Ave", city="LA", country="US")
            ],
            contact=Contact(email="john@example.com"),
            tags={"python", "developer"},
            metadata={"level": 1, "active": True}
        )
        
        serialized = self.serializer.serialize(user)
        deserialized = self.serializer.deserialize(serialized)
        
        assert len(deserialized.addresses) == 2
        assert isinstance(deserialized.tags, set)
        assert deserialized.tags == user.tags
        assert isinstance(deserialized.metadata, dict)
        assert deserialized.metadata == user.metadata

    def test_optional_fields(self):
        """Test handling of optional fields."""
        # Test with optional fields omitted
        address1 = Address(street="123 Main St", city="NYC", country="US")
        serialized1 = self.serializer.serialize(address1)
        deserialized1 = self.serializer.deserialize(serialized1)
        assert deserialized1.location is None
        
        # Test with optional fields included
        address2 = Address(
            street="123 Main St",
            city="NYC",
            country="US",
            location=Location(latitude=40.7128, longitude=-74.0060)
        )
        serialized2 = self.serializer.serialize(address2)
        deserialized2 = self.serializer.deserialize(serialized2)
        assert deserialized2.location is not None
        assert deserialized2.location.latitude == 40.7128

    def test_model_validation_rules(self):
        """Test custom validation rules."""
        # Test country code validation
        with pytest.raises(ValidationError):
            Address(street="123 Main St", city="NYC", country="USA")
        
        # Test coordinate validation
        with pytest.raises(ValidationError):
            Location(latitude=100, longitude=-74.0060)
        
        # Test preferred contact method validation
        with pytest.raises(ValidationError):
            Contact(email="test@example.com", preferred_method="invalid")