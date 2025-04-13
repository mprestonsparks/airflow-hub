"""
Common hooks package for database and API connections that can be shared across projects.
"""

from plugins.common.hooks.database_hook import DatabaseHook
from plugins.common.hooks.api_hook import APIHook

__all__ = ['DatabaseHook', 'APIHook']
