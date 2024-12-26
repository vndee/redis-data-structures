from typing import Any, Dict, Type, Optional, Set, TypeVar
from datetime import datetime, timezone
import json
import logging
from pydantic import BaseModel, create_model, TypeAdapter
from contextlib import contextmanager
from pydantic_core import ValidationError
logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

class ModelRegistry:
    """Registry for managing Pydantic model types and schemas."""
    
    _instance = None
    _models: Dict[str, Type[BaseModel]] = {}
    _schemas: Dict[str, dict] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registered_modules: Set[str] = set()
        return cls._instance
    
    def register_model(self, model: Type[BaseModel]) -> None:
        """Register a Pydantic model and its dependencies."""
        if model.__name__ in self._models:
            return

        # Register the model
        self._models[model.__name__] = model
        self._schemas[model.__name__] = model.model_json_schema()
        
        # Register nested models
        for field in model.model_fields.values():
            if hasattr(field.annotation, '__origin__'):  # Handle generic types
                nested_type = field.annotation.__args__[0]
            else:
                nested_type = field.annotation
                
            if isinstance(nested_type, type) and issubclass(nested_type, BaseModel):
                self.register_model(nested_type)
    
    def get_model(self, model_name: str) -> Optional[Type[BaseModel]]:
        """Get a registered model by name."""
        return self._models.get(model_name)
    
    def get_schema(self, model_name: str) -> Optional[dict]:
        """Get a model's schema by name."""
        return self._schemas.get(model_name)
    
    @contextmanager
    def registration_context(self):
        """Context manager for batch model registration."""
        initial_models = set(self._models.keys())
        try:
            yield
        finally:
            # Clean up any failed registrations
            current_models = set(self._models.keys())
            failed_models = current_models - initial_models
            for model_name in failed_models:
                self._models.pop(model_name, None)
                self._schemas.pop(model_name, None)

class RDSSerializer:
    """Redis Data Structure Serializer for Pydantic models."""
    
    def __init__(self):
        self.registry = ModelRegistry()

    def serialize(self, model: BaseModel) -> str:
        """Serialize a Pydantic model to JSON string."""
        if not isinstance(model, BaseModel):
            raise ValueError("Object is not serializable")

        try:
            # Register the model and its nested dependencies
            self.registry.register_model(model.__class__)
            
            # Create serialized data with type information and schema
            data = {
                "_type": model.__class__.__name__,
                "value": model.model_dump(mode="json"),
                "schema": model.model_json_schema(),
                "nested_types": self._get_nested_types(model.__class__)
            }
            
            # Validate serializable
            try:
                return json.dumps(data)
            except TypeError as e:
                raise ValueError(f"Contains non-serializable nested object: {str(e)}")
                
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            if isinstance(e, (ValueError, ValidationError)):
                raise
            raise ValueError(f"Failed to serialize object: {str(e)}")

    def deserialize(self, data_str: str) -> BaseModel:
        """Deserialize JSON string to Pydantic model."""
        try:
            # Parse JSON
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")

            # Validate data structure
            if not isinstance(data, dict):
                raise ValueError("Invalid serialized data format")

            if "_type" not in data:
                raise ValueError("Invalid serialized data format: missing _type")

            if "value" not in data:
                raise ValueError("Missing value field")

            # Get or create model class
            model_class = self._get_or_create_model(data)
            if model_class is None:
                raise ValueError(f"Unknown model type: {data['_type']}")

            # Validate schema if present
            if "schema" in data:
                stored_schema = data["schema"]
                current_schema = model_class.model_json_schema()
                if not self._validate_schema_compatibility(stored_schema, current_schema):
                    raise ValueError("Schema validation failed")

            # Create TypeAdapter for validation
            adapter = TypeAdapter(model_class)
            
            try:
                return adapter.validate_python(data["value"])
            except ValidationError:
                raise  # Re-raise validation errors as is
            except Exception as e:
                raise ValueError(f"Failed to create model instance: {str(e)}")

        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            if isinstance(e, (ValueError, ValidationError)):
                raise
            raise ValueError(f"Failed to deserialize data: {str(e)}")

    def _get_or_create_model(self, data: dict) -> Optional[Type[BaseModel]]:
        """Get existing model or create dynamic model from schema."""
        model_name = data["_type"]
        
        # Try to get existing model
        model_class = self.registry.get_model(model_name)
        if model_class:
            return model_class

        # Require schema for dynamic model creation
        if "schema" not in data:
            raise ValueError(f"Schema required for unknown model type: {model_name}")

        # Create dynamic model from schema
        with self.registry.registration_context():
            # First create any nested models
            nested_types = data.get("nested_types", {})
            for nested_name, nested_schema in nested_types.items():
                if nested_name not in self.registry._models:
                    try:
                        self._create_dynamic_model(nested_name, nested_schema)
                    except Exception as e:
                        raise ValueError(f"Invalid nested type {nested_name}: {str(e)}")

            # Then create the main model
            try:
                return self._create_dynamic_model(model_name, data["schema"])
            except Exception as e:
                raise ValueError(f"Failed to create model {model_name}: {str(e)}")

    def _validate_schema_compatibility(self, stored_schema: dict, current_schema: dict) -> bool:
        """Validate that stored schema is compatible with current schema."""
        # Compare required fields
        stored_required = set(stored_schema.get("required", []))
        current_required = set(current_schema.get("required", []))
        if not stored_required.issubset(current_required):
            return False

        # Compare property types for common fields
        stored_props = stored_schema.get("properties", {})
        current_props = current_schema.get("properties", {})
        
        for field_name, stored_field in stored_props.items():
            if field_name in current_props:
                current_field = current_props[field_name]
                if stored_field.get("type") != current_field.get("type"):
                    return False

        return True

    def _get_field_type(self, field_schema: dict) -> Any:
        """Get Python type from JSON schema field."""
        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if field_schema.get("type") == "array":
            item_type = self._get_field_type(field_schema["items"])
            return list[item_type]
        
        if "$ref" in field_schema:
            # Handle referenced types (nested models)
            ref_name = field_schema["$ref"].split("/")[-1]
            model = self.registry.get_model(ref_name)
            if model is None:
                raise ValueError(f"Referenced model not found: {ref_name}")
            return model
        
        return type_map.get(field_schema.get("type", "string"), Any)

    def _create_dynamic_model(self, model_name: str, schema: dict) -> Type[BaseModel]:
        """Create a dynamic Pydantic model from schema."""
        fields = {}
        
        for field_name, field_schema in schema.get("properties", {}).items():
            field_type = self._get_field_type(field_schema)
            default = schema.get("default")
            fields[field_name] = (field_type, default)
        
        model = create_model(model_name, **fields)
        self.registry.register_model(model)
        return model

    def _get_nested_types(self, model: Type[BaseModel]) -> Dict[str, dict]:
        """Get all nested type schemas from a model."""
        nested_types = {}
        
        for field in model.model_fields.values():
            if hasattr(field.annotation, '__origin__'):
                nested_type = field.annotation.__args__[0]
            else:
                nested_type = field.annotation
                
            if isinstance(nested_type, type) and issubclass(nested_type, BaseModel):
                nested_types[nested_type.__name__] = nested_type.model_json_schema()
                nested_types.update(self._get_nested_types(nested_type))
        
        return nested_types