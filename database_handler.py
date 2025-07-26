import sqlite3
import pandas as pd
import os
from typing import Dict, List, Any, Optional

class DatabaseHandler:
    """Handles SQLite database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # Test with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            cursor.fetchall()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def get_schema_info(self) -> Dict[str, List[str]]:
        """Get database schema information"""
        schema_info = {}
        
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
            
            cursor = self.connection.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                # Get column information for each table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns_info = cursor.fetchall()
                
                # Format column information
                columns = []
                for col_info in columns_info:
                    col_name = col_info[1]
                    col_type = col_info[2]
                    is_nullable = "NOT NULL" if col_info[3] else "NULL"
                    is_pk = "PRIMARY KEY" if col_info[5] else ""
                    
                    col_description = f"{col_name} ({col_type}) {is_nullable} {is_pk}".strip()
                    columns.append(col_description)
                
                schema_info[table_name] = columns
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting schema info: {e}")
            return {}
    
    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results as DataFrame"""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
            
            # Security check - prevent dangerous operations
            sql_query_upper = sql_query.upper().strip()
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            
            for keyword in dangerous_keywords:
                if keyword in sql_query_upper:
                    print(f"Dangerous SQL operation detected: {keyword}")
                    return None
            
            # Execute the query
            df = pd.read_sql_query(sql_query, self.connection)
            return df
            
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit};"
            return self.execute_query(query)
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return None
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table"""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
            
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            return count
            
        except Exception as e:
            print(f"Error getting row count: {e}")
            return 0
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
        except Exception:
            # Ignore thread-related errors during cleanup
            self.connection = None
    
    def __del__(self):
        """Cleanup database connection"""
        try:
            self.close_connection()
        except Exception:
            pass  # Ignore cleanup errors
        
        # Clean up temporary file if it exists
        if hasattr(self, 'db_path') and self.db_path and os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except:
                pass  # Ignore cleanup errors
