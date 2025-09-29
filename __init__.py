"""
PythonAnywhere Git Pipeline

A Python package for executing git operations on PythonAnywhere hosting service
via their console API using credentials provided through YAML configuration.
"""

from .main import (
    PythonAnywhereGitPipeline,
    PAWCredentials,
    load_credentials_from_yaml,
    load_credentials_from_env,
    load_credentials
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "PythonAnywhereGitPipeline",
    "PAWCredentials", 
    "load_credentials_from_yaml",
    "load_credentials_from_env",
    "load_credentials"
]
