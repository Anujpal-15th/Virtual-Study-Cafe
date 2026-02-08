"""
Custom MySQL backend that bypasses version check for MySQL 5.7
"""
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper


class DatabaseWrapper(MySQLDatabaseWrapper):
    """Custom MySQL database wrapper that allows MySQL 5.7"""
    
    def check_database_version_supported(self):
        """Skip MySQL version check to allow MySQL 5.7"""
        pass
