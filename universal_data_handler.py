import sqlite3
import pandas as pd
import os
import tempfile
import csv
import json
from typing import Dict, List, Any, Optional, Union
import io
import re

# Optional imports for database support
try:
    import pymongo
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

class UniversalDataHandler:
    """Handles various data sources including CSV, JSON, and databases"""
    
    def __init__(self, file_path: str, file_type: str, connection_params: Dict = None):
        self.file_path = file_path
        self.file_type = file_type.lower()
        self.connection_params = connection_params or {}
        self.connection = None
        self.data = None
        self.schema_info = {}
        self.table_names = []
        
    def test_connection(self) -> bool:
        """Test data source connection/validity"""
        try:
            if self.file_type == 'csv':
                return self._test_csv_connection()
            elif self.file_type == 'json':
                return self._test_json_connection()
            elif self.file_type == 'sql':
                return self._test_sql_file_connection()
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._test_sqlite_connection()
            elif self.file_type == 'mysql' and HAS_MYSQL:
                return self._test_mysql_connection()
            elif self.file_type == 'postgresql' and HAS_POSTGRES:
                return self._test_postgres_connection()
            elif self.file_type == 'mongodb' and HAS_MONGO:
                return self._test_mongo_connection()
            else:
                return False
        except Exception as e:
            print(f"Connection test error: {e}")
            return False
    
    def _test_csv_connection(self) -> bool:
        """Test CSV file validity"""
        try:
            # Try to read the CSV file with different encodings
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    self.data = pd.read_csv(self.file_path, encoding=encoding)
                    if len(self.data.columns) > 0:
                        print(f"CSV loaded with {encoding} encoding")
                        return True
                except UnicodeDecodeError:
                    continue
            
            # Try with automatic detection
            self.data = pd.read_csv(self.file_path)
            return len(self.data.columns) > 0
        except Exception as e:
            print(f"CSV test error: {e}")
            return False
    
    def _test_json_connection(self) -> bool:
        """Test JSON file validity"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Handle MongoDB JSON export format (multiple JSON objects per line)
            if content.startswith('{') and '\n{' in content:
                # MongoDB export format - each line is a JSON object
                json_objects = []
                for line in content.strip().split('\n'):
                    if line.strip():
                        try:
                            json_objects.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
                
                if json_objects:
                    self.data = pd.DataFrame(json_objects)
                    return True
            
            # Regular JSON format
            json_data = json.loads(content)
            
            # Convert JSON to DataFrame
            if isinstance(json_data, list):
                self.data = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                # Try to find the main data array
                for key, value in json_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        self.data = pd.DataFrame(value)
                        break
                
                if self.data is None:
                    # Flatten the dict
                    self.data = pd.DataFrame([json_data])
            
            return self.data is not None and len(self.data.columns) > 0
        except Exception as e:
            print(f"JSON test error: {e}")
            return False
    
    def _test_sql_file_connection(self) -> bool:
        """Test SQL file validity and convert to SQLite database"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Create an in-memory SQLite database
            self.connection = sqlite3.connect(':memory:')
            cursor = self.connection.cursor()
            
            # Split SQL content into individual statements
            statements = []
            current_statement = ""
            
            for line in sql_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('--') or line.startswith('/*'):
                    continue
                
                current_statement += line + '\n'
                
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
            
            # Execute SQL statements
            executed_count = 0
            for statement in statements:
                try:
                    # Skip certain PostgreSQL/MySQL specific commands
                    if any(skip_word in statement.upper() for skip_word in ['CREATE DATABASE', 'USE ', 'SET ', 'START TRANSACTION', 'COMMIT']):
                        continue
                    
                    # Convert some common PostgreSQL/MySQL syntax to SQLite
                    statement = self._convert_sql_to_sqlite(statement)
                    
                    cursor.execute(statement)
                    executed_count += 1
                except Exception as e:
                    print(f"Warning: Could not execute statement: {e}")
                    continue
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.table_names = [table[0] for table in tables]
            
            print(f"SQL file processed: {executed_count} statements executed, {len(self.table_names)} tables created")
            return len(self.table_names) > 0
            
        except Exception as e:
            print(f"SQL file test error: {e}")
            return False
    
    def _convert_sql_to_sqlite(self, statement: str) -> str:
        """Convert common SQL syntax to SQLite compatible format"""
        # Convert data types
        type_mappings = {
            'VARCHAR': 'TEXT',
            'CHAR': 'TEXT',
            'LONGTEXT': 'TEXT',
            'MEDIUMTEXT': 'TEXT',
            'TINYTEXT': 'TEXT',
            'BIGINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'TINYINT': 'INTEGER',
            'DECIMAL': 'REAL',
            'DOUBLE': 'REAL',
            'FLOAT': 'REAL',
            'DATETIME': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'DATE': 'TEXT',
            'TIME': 'TEXT'
        }
        
        for old_type, new_type in type_mappings.items():
            statement = re.sub(rf'\b{old_type}\b', new_type, statement, flags=re.IGNORECASE)
        
        # Remove MySQL/PostgreSQL specific syntax
        statement = re.sub(r'ENGINE=\w+', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'DEFAULT CHARSET=\w+', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'COLLATE=\w+', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'AUTO_INCREMENT=\d+', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', statement, flags=re.IGNORECASE)
        
        # Remove backticks (MySQL) and replace with double quotes if needed
        statement = statement.replace('`', '"')
        
        return statement
    
    def _test_sqlite_connection(self) -> bool:
        """Test SQLite database connection"""
        try:
            self.connection = sqlite3.connect(self.file_path)
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.table_names = [table[0] for table in tables]
            return len(self.table_names) > 0
        except Exception as e:
            print(f"SQLite test error: {e}")
            return False
    
    def _test_mysql_connection(self) -> bool:
        """Test MySQL database connection"""
        try:
            self.connection = mysql.connector.connect(**self.connection_params)
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            self.table_names = [table[0] for table in tables]
            return len(self.table_names) > 0
        except Exception as e:
            print(f"MySQL test error: {e}")
            return False
    
    def _test_postgres_connection(self) -> bool:
        """Test PostgreSQL database connection"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            cursor = self.connection.cursor()
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            tables = cursor.fetchall()
            self.table_names = [table[0] for table in tables]
            return len(self.table_names) > 0
        except Exception as e:
            print(f"PostgreSQL test error: {e}")
            return False
    
    def _test_mongo_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            client = pymongo.MongoClient(self.connection_params.get('uri', 'mongodb://localhost:27017/'))
            db = client[self.connection_params.get('database', 'test')]
            self.table_names = db.list_collection_names()
            return len(self.table_names) > 0
        except Exception as e:
            print(f"MongoDB test error: {e}")
            return False
    
    def get_schema_info(self) -> Dict[str, List[str]]:
        """Get data structure information"""
        try:
            if self.file_type in ['csv', 'json']:
                return self._get_file_schema()
            elif self.file_type == 'sql':
                return self._get_sqlite_schema()  # SQL files are converted to SQLite
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._get_sqlite_schema()
            elif self.file_type == 'mysql' and HAS_MYSQL:
                return self._get_mysql_schema()
            elif self.file_type == 'postgresql' and HAS_POSTGRES:
                return self._get_postgres_schema()
            elif self.file_type == 'mongodb' and HAS_MONGO:
                return self._get_mongo_schema()
            else:
                return {}
        except Exception as e:
            print(f"Error getting schema info: {e}")
            return {}
    
    def _get_file_schema(self) -> Dict[str, List[str]]:
        """Get CSV/JSON file structure"""
        if self.data is None:
            if self.file_type == 'csv':
                self._test_csv_connection()
            else:
                self._test_json_connection()
        
        schema_info = {}
        table_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        columns = []
        for col in self.data.columns:
            # Determine data type more accurately
            col_data = self.data[col].dropna()
            if len(col_data) == 0:
                col_type = 'TEXT'
            elif col_data.dtype in ['int64', 'int32', 'int16', 'int8']:
                col_type = 'INTEGER'
            elif col_data.dtype in ['float64', 'float32']:
                col_type = 'REAL'
            elif col_data.dtype == 'bool':
                col_type = 'BOOLEAN'
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_type = 'DATETIME'
            else:
                col_type = 'TEXT'
            
            # Check for nulls
            has_nulls = bool(self.data[col].isnull().any())
            null_info = "NULL" if has_nulls else "NOT NULL"
            
            # Add sample values for better context
            sample_values = col_data.head(3).tolist() if len(col_data) > 0 else []
            sample_str = f" (examples: {sample_values})" if sample_values else ""
            
            col_description = f"{col} ({col_type}) {null_info}{sample_str}"
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
            
            for table_name in self.table_names:
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns_info = cursor.fetchall()
                
                # Get sample data for context
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_rows = cursor.fetchall()
                
                columns = []
                for i, col_info in enumerate(columns_info):
                    col_name = col_info[1]
                    col_type = col_info[2]
                    is_nullable = "NOT NULL" if col_info[3] else "NULL"
                    is_pk = "PRIMARY KEY" if col_info[5] else ""
                    
                    # Add sample values
                    sample_values = [row[i] for row in sample_rows if i < len(row)] if sample_rows else []
                    sample_str = f" (examples: {sample_values[:3]})" if sample_values else ""
                    
                    col_description = f"{col_name} ({col_type}) {is_nullable} {is_pk}{sample_str}".strip()
                    columns.append(col_description)
                
                schema_info[table_name] = columns
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting SQLite schema: {e}")
            return {}
    
    def _get_mysql_schema(self) -> Dict[str, List[str]]:
        """Get MySQL database schema"""
        schema_info = {}
        
        try:
            cursor = self.connection.cursor()
            
            for table_name in self.table_names:
                cursor.execute(f"DESCRIBE {table_name}")
                columns_info = cursor.fetchall()
                
                columns = []
                for col_info in columns_info:
                    col_name = col_info[0]
                    col_type = col_info[1]
                    is_nullable = "NULL" if col_info[2] == 'YES' else "NOT NULL"
                    is_key = f"KEY: {col_info[3]}" if col_info[3] else ""
                    
                    col_description = f"{col_name} ({col_type}) {is_nullable} {is_key}".strip()
                    columns.append(col_description)
                
                schema_info[table_name] = columns
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting MySQL schema: {e}")
            return {}
    
    def _get_postgres_schema(self) -> Dict[str, List[str]]:
        """Get PostgreSQL database schema"""
        schema_info = {}
        
        try:
            cursor = self.connection.cursor()
            
            for table_name in self.table_names:
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """)
                columns_info = cursor.fetchall()
                
                columns = []
                for col_info in columns_info:
                    col_name = col_info[0]
                    col_type = col_info[1]
                    is_nullable = "NULL" if col_info[2] == 'YES' else "NOT NULL"
                    
                    col_description = f"{col_name} ({col_type}) {is_nullable}"
                    columns.append(col_description)
                
                schema_info[table_name] = columns
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting PostgreSQL schema: {e}")
            return {}
    
    def _get_mongo_schema(self) -> Dict[str, List[str]]:
        """Get MongoDB schema (sample-based)"""
        schema_info = {}
        
        try:
            client = pymongo.MongoClient(self.connection_params.get('uri', 'mongodb://localhost:27017/'))
            db = client[self.connection_params.get('database', 'test')]
            
            for collection_name in self.table_names:
                collection = db[collection_name]
                
                # Sample documents to infer schema
                sample_docs = list(collection.find().limit(10))
                
                if sample_docs:
                    # Get all unique fields
                    all_fields = set()
                    for doc in sample_docs:
                        all_fields.update(doc.keys())
                    
                    columns = []
                    for field in sorted(all_fields):
                        # Infer type from samples
                        sample_values = [doc.get(field) for doc in sample_docs if field in doc]
                        field_type = self._infer_mongo_type(sample_values)
                        
                        col_description = f"{field} ({field_type})"
                        columns.append(col_description)
                    
                    schema_info[collection_name] = columns
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting MongoDB schema: {e}")
            return {}
    
    def _infer_mongo_type(self, values: List[Any]) -> str:
        """Infer MongoDB field type from sample values"""
        if not values:
            return "UNKNOWN"
        
        types = set()
        for val in values:
            if val is None:
                continue
            elif isinstance(val, bool):
                types.add("BOOLEAN")
            elif isinstance(val, int):
                types.add("INTEGER")
            elif isinstance(val, float):
                types.add("REAL")
            elif isinstance(val, str):
                types.add("TEXT")
            elif isinstance(val, list):
                types.add("ARRAY")
            elif isinstance(val, dict):
                types.add("OBJECT")
            else:
                types.add("MIXED")
        
        return "/".join(sorted(types)) if types else "NULL"
    
    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query and return results as DataFrame"""
        try:
            # Security check
            if not self._is_safe_query(sql_query):
                print("Dangerous SQL operation detected")
                return None
            
            if self.file_type in ['csv', 'json']:
                return self._execute_file_query(sql_query)
            elif self.file_type == 'sql':
                return self._execute_sqlite_query(sql_query)  # SQL files use SQLite
            elif self.file_type in ['sqlite', 'sqlite3', 'db']:
                return self._execute_sqlite_query(sql_query)
            elif self.file_type == 'mysql' and HAS_MYSQL:
                return self._execute_mysql_query(sql_query)
            elif self.file_type == 'postgresql' and HAS_POSTGRES:
                return self._execute_postgres_query(sql_query)
            elif self.file_type == 'mongodb' and HAS_MONGO:
                return self._execute_mongo_query(sql_query)
            else:
                return None
                
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def _execute_file_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on CSV/JSON data using SQLite in memory"""
        try:
            if self.data is None:
                if self.file_type == 'csv':
                    self._test_csv_connection()
                else:
                    self._test_json_connection()
            
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Get table name from file
            table_name = os.path.splitext(os.path.basename(self.file_path))[0]
            
            # Clean column names to avoid SQL issues
            cleaned_data = self.data.copy()
            column_mapping = {}
            
            for col in cleaned_data.columns:
                # Create safe column names
                safe_col = re.sub(r'[^a-zA-Z0-9_]', '_', str(col).strip())
                safe_col = re.sub(r'_+', '_', safe_col)  # Replace multiple underscores
                safe_col = safe_col.strip('_')  # Remove leading/trailing underscores
                
                if not safe_col or safe_col.isdigit():
                    safe_col = f"col_{safe_col}"
                
                if safe_col != col:
                    column_mapping[col] = safe_col
                    cleaned_data = cleaned_data.rename(columns={col: safe_col})
            
            # Load data into SQLite with cleaned column names
            cleaned_data.to_sql(table_name, conn, index=False, if_exists='replace')
            
            # Get actual column names from the created table
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            actual_columns = [row[1] for row in cursor.fetchall()]
            
            # Enhanced query fixing
            modified_query = self._fix_query_for_columns(sql_query, actual_columns, column_mapping, table_name)
            
            print(f"Original query: {sql_query}")
            print(f"Modified query: {modified_query}")
            print(f"Available columns: {actual_columns}")
            
            # Execute the query
            result = pd.read_sql_query(modified_query, conn)
            conn.close()
            
            # Restore original column names in result
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            for safe_col, original_col in reverse_mapping.items():
                if safe_col in result.columns:
                    result = result.rename(columns={safe_col: original_col})
            
            return result
            
        except Exception as e:
            print(f"Error executing file query: {e}")
            # Fallback: return sample data
            try:
                if self.data is not None:
                    return self.data.head(10)
            except:
                pass
            return None
    
    def _fix_query_for_columns(self, sql_query: str, actual_columns: List[str], column_mapping: Dict[str, str], table_name: str) -> str:
        """Enhanced query fixing for column and table name issues"""
        modified_query = sql_query
        
        # Replace original column names with safe names
        for original_col, safe_col in column_mapping.items():
            # Handle quoted column names
            patterns = [
                f'"{original_col}"',
                f"'{original_col}'",
                f"`{original_col}`",
                f" {original_col} ",
                f" {original_col},",
                f" {original_col}\n",
                f"({original_col})",
                f".{original_col}",
            ]
            
            for pattern in patterns:
                if pattern in modified_query:
                    replacement = pattern.replace(original_col, safe_col)
                    modified_query = modified_query.replace(pattern, replacement)
        
        # Replace common table name placeholders
        table_placeholders = ['csv_data', 'data', 'table', 'file']
        for placeholder in table_placeholders:
            modified_query = re.sub(rf'\b{placeholder}\b', table_name, modified_query, flags=re.IGNORECASE)
        
        # Try to match columns with case-insensitive approach
        for actual_col in actual_columns:
            # Find similar column references in different cases
            pattern = rf'\b{re.escape(actual_col)}\b'
            matches = re.findall(pattern, modified_query, re.IGNORECASE)
            for match in matches:
                if match != actual_col:
                    modified_query = modified_query.replace(match, actual_col)
        
        return modified_query
    
    def _execute_sqlite_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on SQLite database"""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.file_path)
            
            df = pd.read_sql_query(sql_query, self.connection)
            return df
            
        except Exception as e:
            print(f"Error executing SQLite query: {e}")
            return None
    
    def _execute_mysql_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on MySQL database"""
        try:
            df = pd.read_sql_query(sql_query, self.connection)
            return df
        except Exception as e:
            print(f"Error executing MySQL query: {e}")
            return None
    
    def _execute_postgres_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute query on PostgreSQL database"""
        try:
            df = pd.read_sql_query(sql_query, self.connection)
            return df
        except Exception as e:
            print(f"Error executing PostgreSQL query: {e}")
            return None
    
    def _execute_mongo_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Convert SQL-like query to MongoDB and execute (basic implementation)"""
        try:
            # This is a simplified implementation
            # In practice, you'd need a more sophisticated SQL-to-MongoDB translator
            client = pymongo.MongoClient(self.connection_params.get('uri', 'mongodb://localhost:27017/'))
            db = client[self.connection_params.get('database', 'test')]
            
            # Basic pattern matching for simple queries
            # This is very limited and would need expansion for production use
            if 'SELECT * FROM' in sql_query.upper():
                table_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
                if table_match:
                    collection_name = table_match.group(1)
                    collection = db[collection_name]
                    
                    # Handle LIMIT
                    limit_match = re.search(r'LIMIT\s+(\d+)', sql_query, re.IGNORECASE)
                    limit = int(limit_match.group(1)) if limit_match else 100
                    
                    docs = list(collection.find().limit(limit))
                    return pd.DataFrame(docs)
            
            return None
        except Exception as e:
            print(f"Error executing MongoDB query: {e}")
            return None
    
    def _is_safe_query(self, sql_query: str) -> bool:
        """Check if query is safe to execute"""
        sql_query_upper = sql_query.upper().strip()
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        
        for keyword in dangerous_keywords:
            if keyword in sql_query_upper:
                return False
        
        return True
    
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
            if self.file_type in ['csv', 'json']:
                # For files, use the data length
                if self.data is not None:
                    info['total_rows'] = len(self.data)
                    table_name = list(schema.keys())[0] if schema else 'data'
                    info['tables'][table_name] = {
                        'columns': len(self.data.columns),
                        'rows': len(self.data)
                    }
            elif self.file_type == 'sql':
                # For SQL files, count rows in each table
                for table_name in schema.keys():
                    try:
                        if self.connection:
                            cursor = self.connection.cursor()
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                            row_count = cursor.fetchone()[0]
                            info['tables'][table_name] = {
                                'columns': len(schema[table_name]),
                                'rows': row_count
                            }
                            info['total_rows'] += row_count
                    except Exception as e:
                        print(f"Error getting row count for {table_name}: {e}")
                        info['tables'][table_name] = {
                            'columns': len(schema[table_name]),
                            'rows': 0
                        }
            else:
                # For databases, count rows in each table/collection
                for table_name in schema.keys():
                    try:
                        if self.file_type in ['sqlite', 'sqlite3', 'db']:
                            if not self.connection:
                                self.connection = sqlite3.connect(self.file_path)
                            cursor = self.connection.cursor()
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                            row_count = cursor.fetchone()[0]
                        elif self.file_type == 'mysql' and HAS_MYSQL:
                            cursor = self.connection.cursor()
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                            row_count = cursor.fetchone()[0]
                        elif self.file_type == 'postgresql' and HAS_POSTGRES:
                            cursor = self.connection.cursor()
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                            row_count = cursor.fetchone()[0]
                        elif self.file_type == 'mongodb' and HAS_MONGO:
                            client = pymongo.MongoClient(self.connection_params.get('uri', 'mongodb://localhost:27017/'))
                            db = client[self.connection_params.get('database', 'test')]
                            collection = db[table_name]
                            row_count = collection.count_documents({})
                        else:
                            row_count = 0
                        
                        info['tables'][table_name] = {
                            'columns': len(schema[table_name]),
                            'rows': row_count
                        }
                        info['total_rows'] += row_count
                        
                    except Exception as e:
                        print(f"Error getting row count for {table_name}: {e}")
                        info['tables'][table_name] = {
                            'columns': len(schema[table_name]),
                            'rows': 0
                        }
            
        except Exception as e:
            print(f"Error getting data info: {e}")
        
        return info
    
    def get_sample_data(self, table_name: Optional[str] = None, limit: int = 5) -> Optional[pd.DataFrame]:
        """Get sample data"""
        try:
            if self.file_type in ['csv', 'json']:
                if self.data is None:
                    if self.file_type == 'csv':
                        self._test_csv_connection()
                    else:
                        self._test_json_connection()
                return self.data.head(limit) if self.data is not None else None
            elif self.file_type in ['sql', 'sqlite', 'sqlite3', 'db']:
                if table_name and table_name in self.table_names:
                    query = f"SELECT * FROM {table_name} LIMIT {limit};"
                    return self.execute_query(query)
                elif self.table_names:
                    # Return sample from first table if no specific table requested
                    query = f"SELECT * FROM {self.table_names[0]} LIMIT {limit};"
                    return self.execute_query(query)
            else:
                if table_name and table_name in self.table_names:
                    query = f"SELECT * FROM {table_name} LIMIT {limit};"
                    return self.execute_query(query)
            return None
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return None
    
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