import requests
import json
from typing import Dict, List, Optional

class QueryGenerator:
    """Generates SQL queries from natural language using OpenRouter.ai"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_sql(self, user_query: str, schema_info: Dict[str, List[str]]) -> Optional[str]:
        """Generate SQL query from natural language"""
        try:
            # Create schema context
            schema_context = self._format_schema_context(schema_info)
            
            # Create the prompt
            prompt = self._create_sql_prompt(user_query, schema_context)
            
            # Make API call
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert SQL query generator. Generate only valid SQLite queries based on the provided schema. Return only the SQL query without any explanations or formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sql_query = result['choices'][0]['message']['content'].strip()
                
                # Clean up the SQL query
                sql_query = self._clean_sql_query(sql_query)
                
                return sql_query
            else:
                print(f"API Error: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return None
    
    def _format_schema_context(self, schema_info: Dict[str, List[str]]) -> str:
        """Format schema information for the prompt"""
        schema_text = "Database Schema:\n"
        
        for table_name, columns in schema_info.items():
            schema_text += f"\nTable: {table_name}\n"
            for column in columns:
                schema_text += f"  - {column}\n"
        
        return schema_text
    
    def _create_sql_prompt(self, user_query: str, schema_context: str) -> str:
        """Create the complete prompt for SQL generation"""
        prompt = f"""
{schema_context}

User Question: {user_query}

Generate a SQLite query to answer this question. Requirements:
1. Use only SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper table and column names from the schema above
3. Include appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
4. Return only the SQL query, no explanations
5. Use SQLite-compatible syntax

SQL Query:
"""
        return prompt
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate the generated SQL query"""
        # Remove common formatting artifacts
        sql_query = sql_query.strip()
        
        # Remove markdown code blocks if present
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        # Remove extra whitespace
        sql_query = sql_query.strip()
        
        # Ensure query ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        return sql_query
    
    def validate_sql_safety(self, sql_query: str) -> bool:
        """Validate that the SQL query is safe to execute"""
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 
            'CREATE', 'TRUNCATE', 'REPLACE', 'ATTACH', 'DETACH'
        ]
        
        sql_upper = sql_query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True
