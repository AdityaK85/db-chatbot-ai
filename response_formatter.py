import requests
import json
import pandas as pd
from typing import Dict, List, Any, Optional

class ResponseFormatter:
    """Formats query results into conversational responses using OpenRouter.ai"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def format_response(self, user_query: str, sql_query: str, results: pd.DataFrame, schema_info: Dict[str, List[str]]) -> str:
        """Format query results into a conversational response"""
        try:
            # If no results, provide a helpful response
            if results.empty:
                return self._generate_no_results_response(user_query)
            
            # Format the results data
            results_summary = self._format_results_summary(results)
            
            # Generate conversational response
            conversational_response = self._generate_conversational_response(
                user_query, sql_query, results_summary, results
            )
            
            # Add the actual data display
            formatted_response = conversational_response + "\n\n" + self._format_data_display(results)
            
            # Add follow-up suggestions if appropriate
            suggestions = self._generate_follow_up_suggestions(user_query, results, schema_info)
            if suggestions:
                formatted_response += "\n\n" + suggestions
            
            return formatted_response
            
        except Exception as e:
            print(f"Error formatting response: {e}")
            return f"I found some results for your query, but had trouble formatting the response. Here's what I found:\n\n{self._format_data_display(results)}"
    
    def _format_results_summary(self, results: pd.DataFrame) -> str:
        """Create a summary of the results"""
        summary = f"Found {len(results)} record(s)"
        
        if len(results) > 0:
            # Add basic statistics for numeric columns
            numeric_cols = results.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = []
                for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    total = results[col].sum()
                    avg = results[col].mean()
                    stats.append(f"{col}: total={total:.2f}, avg={avg:.2f}")
                
                if stats:
                    summary += f"\nNumeric summary: {', '.join(stats)}"
        
        return summary
    
    def _generate_conversational_response(self, user_query: str, sql_query: str, results_summary: str, results: pd.DataFrame) -> str:
        """Generate a conversational response using AI"""
        try:
            # Create sample data for context (limit to first few rows)
            sample_data = results.head(3).to_string(index=False) if not results.empty else "No data"
            
            prompt = f"""
User asked: "{user_query}"
SQL query executed: {sql_query}
Results summary: {results_summary}
Sample data:
{sample_data}

Create a natural, conversational response that:
1. Directly answers the user's question
2. Mentions specific numbers/counts from the results
3. Is friendly and helpful
4. Sounds natural, like a human assistant
5. Keeps it concise but informative
6. Uses the actual data from the results

Response:
"""
            
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful database assistant. Provide natural, conversational responses about database query results. Be specific with numbers and data from the results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                # Fallback response
                return self._generate_fallback_response(user_query, results)
                
        except Exception as e:
            print(f"Error generating conversational response: {e}")
            return self._generate_fallback_response(user_query, results)
    
    def _generate_fallback_response(self, user_query: str, results: pd.DataFrame) -> str:
        """Generate a simple fallback response"""
        if results.empty:
            return "I couldn't find any results for your question."
        
        count = len(results)
        if count == 1:
            return f"I found 1 result for your question."
        else:
            return f"I found {count} results for your question."
    
    def _generate_no_results_response(self, user_query: str) -> str:
        """Generate response when no results are found"""
        return f"I couldn't find any data matching your question: '{user_query}'. You might want to try rephrasing your question or check if the data exists in the database."
    
    def _format_data_display(self, results: pd.DataFrame) -> str:
        """Format the actual data for display"""
        if results.empty:
            return "No data to display."
        
        # Limit the number of rows displayed
        max_rows = 10
        display_results = results.head(max_rows)
        
        # Convert to string with proper formatting
        data_str = display_results.to_string(index=False, max_cols=10)
        
        # Add indication if there are more rows
        if len(results) > max_rows:
            data_str += f"\n\n... and {len(results) - max_rows} more rows"
        
        return f"**Data Results:**\n```\n{data_str}\n```"
    
    def _generate_follow_up_suggestions(self, user_query: str, results: pd.DataFrame, schema_info: Dict[str, List[str]]) -> str:
        """Generate follow-up question suggestions"""
        if results.empty:
            return ""
        
        suggestions = []
        
        # Basic suggestions based on result type
        if len(results) > 1:
            suggestions.append("Would you like to see more details about any specific item?")
            suggestions.append("Do you want to filter these results further?")
        
        # Suggestions based on columns
        if not results.empty:
            columns = results.columns.tolist()
            
            # Suggest sorting if there are multiple rows
            if len(results) > 1 and len(columns) > 1:
                suggestions.append(f"Would you like me to sort these by {columns[0]} or {columns[1]}?")
            
            # Suggest analysis for numeric columns
            numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                suggestions.append(f"Want to see statistics or analysis of {numeric_cols[0]}?")
        
        if suggestions:
            # Limit to 2 suggestions
            selected_suggestions = suggestions[:2]
            return "**Follow-up suggestions:**\n" + "\n".join([f"• {s}" for s in selected_suggestions])
        
        return ""
