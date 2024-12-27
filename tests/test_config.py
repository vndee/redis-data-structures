from unittest.mock import MagicMock, patch

import pytest

from redis_data_structures.config import Config, DataStructureConfig, RedisConfig
from redis_data_structures.exceptions import ConfigurationError


def test_redis_config_validation():
    """Test RedisConfig validation."""
    config = RedisConfig(
        host="localhost",
        port=6379,
        db=0,
        password="password",  # noqa: S106
        ssl=False,
        max_connections=10,
    )
    assert config.host == "localhost"
    assert config.port == 6379
    assert config.db == 0
    assert config.password == "password"  # noqa: S105
    assert config.ssl is False
    assert config.max_connections == 10

    # Test invalid port
    with pytest.raises(ConfigurationError):
        RedisConfig(port=70000)

    # Test invalid db
    with pytest.raises(ConfigurationError):
        RedisConfig(db=-1)

    # Test invalid max connections
    with pytest.raises(ConfigurationError):
        RedisConfig(max_connections=0)


def test_data_structure_config():
    """Test DataStructureConfig defaults."""
    ds_config = DataStructureConfig()
    assert ds_config.prefix == "redis_ds"
    assert ds_config.compression_threshold == 1024
    assert ds_config.debug_enabled is False


def test_config_from_yaml(tmp_path):
    """Test creating Config from a YAML file."""
    yaml_content = """
    redis:
      host: localhost
      port: 6379
      db: 0
      password: password
      ssl: false
      max_connections: 10
    data_structures:
      prefix: redis_ds
      compression_threshold: 1024
      debug_enabled: false
    """
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content)

    config = Config.from_yaml(str(yaml_file))
    assert config.redis.host == "localhost"
    assert config.redis.port == 6379
    assert config.redis.db == 0
    assert config.redis.password == "password"  # noqa: S105
    assert config.redis.ssl is False
    assert config.redis.max_connections == 10
    assert config.data_structures.prefix == "redis_ds"
    assert config.data_structures.compression_threshold == 1024
    assert config.data_structures.debug_enabled is False


def test_config_from_yaml_invalid(tmp_path):
    """Test handling of invalid YAML configuration."""
    invalid_yaml_content = """
    redis:
      host: localhost
      port: invalid_port
    """
    yaml_file = tmp_path / "invalid_config.yaml"
    yaml_file.write_text(invalid_yaml_content)

    with pytest.raises(ConfigurationError):
        Config.from_yaml(str(yaml_file))


def test_from_yaml_load_error():
    """Test loading configuration from YAML file raises ConfigurationError."""
    with patch("yaml.safe_load", side_effect=Exception("YAML load error")), pytest.raises(
        ConfigurationError,
        match="Failed to load configuration from",
    ):
        Config.from_yaml("invalid_path.yaml")


def test_to_dict():
    """Test converting configuration to dictionary."""
    config = Config(
        redis=MagicMock(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            ssl=False,
            max_connections=10,
        ),
        data_structures=DataStructureConfig(
            prefix="test_prefix",
            compression_threshold=1024,
            debug_enabled=False,
        ),
    )
    expected_dict = {
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0,  # Ensure this matches the mock
            "password": None,
            "ssl": False,
            "max_connections": 10,
        },
        "data_structures": {
            "prefix": "test_prefix",
            "compression_threshold": 1024,
            "debug_enabled": False,
        },
    }
    assert config.to_dict() == expected_dict


def test_validate_compression_threshold_error():
    """Test validation raises ConfigurationError for invalid compression threshold."""
    config = Config(
        redis=MagicMock(),
        data_structures=DataStructureConfig(compression_threshold=-1),
    )
    with pytest.raises(ConfigurationError, match="Invalid compression threshold"):
        config.validate()
