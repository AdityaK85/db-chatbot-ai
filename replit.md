# Data Chatbot Agent

## Overview

This is a Streamlit-based data chatbot application that allows users to upload CSV files or SQLite databases and interact with them using natural language queries. The system leverages OpenRouter.ai's API to convert natural language questions into SQL queries and format the results into conversational responses.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interaction
- **Database Layer**: SQLite database handling with schema introspection
- **AI Integration**: OpenRouter.ai API for natural language processing
- **Query Processing**: Dedicated modules for SQL generation and response formatting

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Streamlit frontend and application orchestration
- **Features**: File upload, chat interface, session state management
- **Technology**: Streamlit framework for web UI

### 2. Data Handler (`data_handler.py`)
- **Purpose**: Multi-format data operations and schema management
- **Features**: CSV and SQLite support, connection testing, schema introspection, query execution
- **Technology**: sqlite3 with pandas for data manipulation, in-memory SQLite for CSV queries

### 3. Query Generator (`query_generator.py`)
- **Purpose**: Convert natural language to SQL queries
- **Features**: OpenRouter.ai integration, schema-aware query generation
- **Model**: OpenAI GPT-3.5-turbo via OpenRouter.ai

### 4. Response Formatter (`response_formatter.py`)
- **Purpose**: Format query results into conversational responses
- **Features**: Natural language response generation, data visualization, follow-up suggestions
- **Technology**: OpenRouter.ai API with pandas for data processing

## Data Flow

1. **Data Upload**: User uploads CSV file or SQLite database file
2. **Schema Analysis**: System extracts data structures and column information
3. **Natural Language Input**: User asks questions in plain English
4. **Query Generation**: AI converts question to SQL using schema context
5. **Query Execution**: SQL query runs against the uploaded data (in-memory SQLite for CSV)
6. **Response Formatting**: Results are formatted into conversational responses
7. **Display**: Formatted response and data are presented to the user

## External Dependencies

### AI Services
- **OpenRouter.ai**: Primary AI service for natural language processing
- **Model**: OpenAI GPT-3.5-turbo for both query generation and response formatting
- **Authentication**: API key-based authentication

### Python Libraries
- **Streamlit**: Web application framework
- **sqlite3**: Database connectivity
- **pandas**: Data manipulation and analysis
- **requests**: HTTP client for API calls

## Deployment Strategy

### Local Development
- Python environment with required dependencies
- Environment variable for OpenRouter.ai API key
- Streamlit development server

### Production Considerations
- Session state management for multi-user scenarios
- Temporary file handling for database uploads
- API rate limiting and error handling
- Security considerations for uploaded database files

### Environment Variables
- `OPENROUTER_API_KEY`: Required for AI service integration
- Fallback hardcoded key provided for development (should be replaced in production)

## Architecture Decisions

### Data Sources: CSV and SQLite
- **CSV Support**: Added support for CSV files using in-memory SQLite conversion
- **SQLite Support**: Lightweight, file-based database suitable for upload scenarios
- **Pros**: No server setup required, easy file handling, supports multiple data formats
- **Cons**: Limited to single-user scenarios, file size limitations for large datasets

### AI Service: OpenRouter.ai
- **Rationale**: Provides access to multiple AI models through unified API
- **Pros**: Model flexibility, competitive pricing, good reliability
- **Cons**: External dependency, API costs, rate limiting

### Frontend: Streamlit
- **Rationale**: Rapid development of data-focused web applications
- **Pros**: Python-native, built-in widgets, easy deployment
- **Cons**: Limited customization, session state complexity

### Modular Architecture
- **Rationale**: Separation of concerns for maintainability
- **Pros**: Testable components, clear responsibilities, easy to extend
- **Cons**: Slight complexity overhead for small applications