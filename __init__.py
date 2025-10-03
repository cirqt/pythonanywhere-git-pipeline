"""
PythonAnywhere Git Pipeline

A Python package for executing git operations on PythonAnywhere hosting service
via their console API using credentials provided through YAML configuration.
"""

try:
    from .main import (
        PythonAnywhereGitPipeline,
        PAWCredentials,
        load_credentials_from_yaml,
        load_credentials_from_env,
        load_credentials
    )
except ImportError:
    # Fallback for when run as script or in tests
    from main import (
        PythonAnywhereGitPipeline,
        PAWCredentials,
        load_credentials_from_yaml,
        load_credentials_from_env,
        load_credentials
    )

__all__ = [
    "PythonAnywhereGitPipeline",
    "PAWCredentials", 
    "load_credentials_from_yaml",
    "load_credentials_from_env",
    "load_credentials"
]
