import streamlit as st
import sqlite3
import os
import tempfile
from database_handler import DatabaseHandler
from query_generator import QueryGenerator
from response_formatter import ResponseFormatter

# Page configuration
st.set_page_config(
    page_title="SQL Chatbot Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_handler" not in st.session_state:
    st.session_state.db_handler = None
if "query_generator" not in st.session_state:
    st.session_state.query_generator = None
if "response_formatter" not in st.session_state:
    st.session_state.response_formatter = None
if "database_connected" not in st.session_state:
    st.session_state.database_connected = False

def initialize_components():
    """Initialize the chatbot components"""
    api_key = os.getenv("OPENROUTER_API_KEY", "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")
    st.session_state.query_generator = QueryGenerator(api_key)
    st.session_state.response_formatter = ResponseFormatter(api_key)

def handle_database_upload(uploaded_file):
    """Handle SQLite database file upload"""
    if uploaded_file is not None:
        try:
            # Create a temporary file to store the uploaded database
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_db_path = temp_file.name
            
            # Initialize database handler
            st.session_state.db_handler = DatabaseHandler(temp_db_path)
            
            # Test connection and get schema info
            if st.session_state.db_handler.test_connection():
                st.session_state.database_connected = True
                schema_info = st.session_state.db_handler.get_schema_info()
                
                st.success(f"✅ Database connected successfully!")
                st.info(f"📊 Found {len(schema_info)} tables: {', '.join(schema_info.keys())}")
                
                # Add welcome message
                welcome_msg = f"Hello! I'm your SQL assistant. I've connected to your database with {len(schema_info)} tables. You can ask me questions about your data in natural language, and I'll help you query it!"
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                
                return True
            else:
                st.error("❌ Failed to connect to the database. Please ensure it's a valid SQLite file.")
                return False
                
        except Exception as e:
            st.error(f"❌ Error processing database file: {str(e)}")
            return False
    return False

def process_user_query(user_input):
    """Process user query and generate response"""
    if not st.session_state.database_connected or not st.session_state.db_handler:
        return "Please upload a SQLite database first."
    
    try:
        # Get database schema for context
        schema_info = st.session_state.db_handler.get_schema_info()
        
        # Generate SQL query
        with st.spinner("🤔 Understanding your question..."):
            sql_query = st.session_state.query_generator.generate_sql(user_input, schema_info)
        
        if not sql_query:
            return "I couldn't understand your question. Could you please rephrase it?"
        
        # Execute query
        with st.spinner("🔍 Querying your database..."):
            query_results = st.session_state.db_handler.execute_query(sql_query)
        
        if query_results is None:
            return "I encountered an error while executing the query. Please try rephrasing your question."
        
        # Format response
        with st.spinner("✨ Formatting response..."):
            formatted_response = st.session_state.response_formatter.format_response(
                user_input, sql_query, query_results, schema_info
            )
        
        return formatted_response
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return "I encountered an error while processing your request. Please try again."

def main():
    st.title("🤖 SQL Chatbot Agent")
    st.markdown("Upload your SQLite database and chat with your data using natural language!")
    
    # Initialize components
    initialize_components()
    
    # Sidebar for database upload
    with st.sidebar:
        st.header("📁 Database Upload")
        uploaded_file = st.file_uploader(
            "Choose your SQLite database file",
            type=['db', 'sqlite', 'sqlite3'],
            help="Upload a SQLite database file to start chatting with your data"
        )
        
        if uploaded_file:
            if handle_database_upload(uploaded_file):
                st.success("Database ready for queries!")
        
        # Database info
        if st.session_state.database_connected and st.session_state.db_handler:
            st.header("📊 Database Info")
            schema_info = st.session_state.db_handler.get_schema_info()
            
            for table_name, columns in schema_info.items():
                with st.expander(f"Table: {table_name}"):
                    for col in columns:
                        st.text(f"• {col}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with your Database")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your database..."):
        if not st.session_state.database_connected:
            st.warning("⚠️ Please upload a SQLite database first!")
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = process_user_query(prompt)
                st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
