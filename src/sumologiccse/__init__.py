"""
Sumo Logic Cloud SIEM Python SDK

A Python client library for the Sumo Logic Cloud SIEM API.
"""

from .sumologiccse import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DataError,
    SumoLogicCSE,
    SumoLogicCSEError,
)

__version__ = "0.2.0"
__all__ = [
    "SumoLogicCSE",
    "SumoLogicCSEError",
    "AuthenticationError",
    "APIError",
    "ConfigurationError",
    "DataError",
]
