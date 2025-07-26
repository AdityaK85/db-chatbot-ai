import sqlite3
import pandas as pd
import os
import tempfile
import csv
from typing import Dict, List, Any, Optional, Union
import io

class DataHandler:
    """Handles various data sources including CSV files and databases"""
    
    def __init__(self, file_path: str, file_type: str):
        self.file_path = file_path
        self.file_type = file_type.lower()
        self.connection = None
        self.data = None
        self.schema_info = {}
        
    def test_connection(self) -> bool:
        """Test data source connection/validity"""
        try:
            if self.file_type == 'csv':
                return self._test_csv_connection()
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._test_sqlite_connection()
            else:
                return False
        except Exception as e:
            print(f"Connection test error: {e}")
            return False
    
    def _test_csv_connection(self) -> bool:
        """Test CSV file validity"""
        try:
            # Try to read the CSV file
            self.data = pd.read_csv(self.file_path)
            return len(self.data.columns) > 0
        except Exception as e:
            print(f"CSV test error: {e}")
            return False
    
    def _test_sqlite_connection(self) -> bool:
        """Test SQLite database connection"""
        try:
            self.connection = sqlite3.connect(self.file_path)
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            cursor.fetchall()
            return True
        except Exception as e:
            print(f"SQLite test error: {e}")
            return False
    
    def get_schema_info(self) -> Dict[str, List[str]]:
        """Get data structure information"""
        try:
            if self.file_type == 'csv':
                return self._get_csv_schema()
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._get_sqlite_schema()
            else:
                return {}
        except Exception as e:
            print(f"Error getting schema info: {e}")
            return {}
    
    def _get_csv_schema(self) -> Dict[str, List[str]]:
        """Get CSV file structure"""
        if self.data is None:
            self.data = pd.read_csv(self.file_path)
        
        schema_info = {}
        table_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        columns = []
        for col in self.data.columns:
            # Determine data type
            dtype = str(self.data[col].dtype)
            if dtype.startswith('int'):
                col_type = 'INTEGER'
            elif dtype.startswith('float'):
                col_type = 'REAL'
            elif dtype.startswith('bool'):
                col_type = 'BOOLEAN'
            else:
                col_type = 'TEXT'
            
            # Check for nulls
            has_nulls = bool(self.data[col].isnull().any())
            null_info = "NULL" if has_nulls else "NOT NULL"
            
            col_description = f"{col} ({col_type}) {null_info}"
            columns.append(col_description)
        
        schema_info[table_name] = columns
        return schema_info
    
    def _get_sqlite_schema(self) -> Dict[str, List[str]]:
        """Get SQLite database schema"""
        schema_info = {}
        
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.file_path)
            
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
            print(f"Error getting SQLite schema: {e}")
            return {}
    
    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query and return results as DataFrame"""
        try:
            # Security check - prevent dangerous operations
            if not self._is_safe_query(sql_query):
                print("Dangerous SQL operation detected")
                return None
            
            if self.file_type == 'csv':
                return self._execute_csv_query(sql_query)
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._execute_sqlite_query(sql_query)
            else:
                return None
                
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def _execute_csv_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on CSV data using SQLite in memory"""
        try:
            if self.data is None:
                self.data = pd.read_csv(self.file_path)
            
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Get table name from file
            table_name = os.path.splitext(os.path.basename(self.file_path))[0]
            
            # Load CSV data into SQLite
            self.data.to_sql(table_name, conn, index=False, if_exists='replace')
            
            # Replace any table references in the query
            modified_query = sql_query.replace('csv_data', table_name)
            if table_name not in modified_query.lower():
                # If query doesn't reference our table, try to add it
                if 'from' in modified_query.lower() and table_name not in modified_query.lower():
                    # This is a basic replacement - might need more sophisticated parsing
                    pass
            
            # Execute the query
            result = pd.read_sql_query(modified_query, conn)
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error executing CSV query: {e}")
            return None
    
    def _execute_sqlite_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on SQLite database"""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.file_path)
            
            # Execute the query
            df = pd.read_sql_query(sql_query, self.connection)
            return df
            
        except Exception as e:
            print(f"Error executing SQLite query: {e}")
            return None
    
    def _is_safe_query(self, sql_query: str) -> bool:
        """Check if query is safe to execute"""
        sql_query_upper = sql_query.upper().strip()
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        
        for keyword in dangerous_keywords:
            if keyword in sql_query_upper:
                return False
        
        return True
    
    def get_sample_data(self, table_name: Optional[str] = None, limit: int = 5) -> Optional[pd.DataFrame]:
        """Get sample data"""
        try:
            if self.file_type == 'csv':
                if self.data is None:
                    self.data = pd.read_csv(self.file_path)
                return self.data.head(limit)
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                if table_name:
                    query = f"SELECT * FROM {table_name} LIMIT {limit};"
                    return self.execute_query(query)
            return None
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return None
    
    def get_table_row_count(self, table_name: Optional[str] = None) -> int:
        """Get row count"""
        try:
            if self.file_type == 'csv':
                if self.data is None:
                    self.data = pd.read_csv(self.file_path)
                return len(self.data)
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                if table_name:
                    if not self.connection:
                        self.connection = sqlite3.connect(self.file_path)
                    cursor = self.connection.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    return count
            return 0
        except Exception as e:
            print(f"Error getting row count: {e}")
            return 0
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get general information about the data"""
        info = {
            'file_type': self.file_type,
            'file_path': self.file_path,
            'tables': {},
            'total_rows': 0
        }
        
        try:
            schema = self.get_schema_info()
            for table_name in schema.keys():
                row_count = self.get_table_row_count(table_name)
                info['tables'][table_name] = {
                    'columns': len(schema[table_name]),
                    'rows': row_count
                }
                info['total_rows'] += row_count
            
        except Exception as e:
            print(f"Error getting data info: {e}")
        
        return info
    
    def close_connection(self):
        """Close connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
        except Exception:
            self.connection = None
    
    def __del__(self):
        """Cleanup"""
        try:
            self.close_connection()
        except Exception:
            pass
        
        # Clean up temporary file if it exists
        if hasattr(self, 'file_path') and self.file_path and os.path.exists(self.file_path):
            try:
                if self.file_path.startswith('/tmp/') or 'tmp' in self.file_path:
                    os.unlink(self.file_path)
            except:
                pass