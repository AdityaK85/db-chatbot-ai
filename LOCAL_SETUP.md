# Local Setup Guide - Data Chatbot Agent

## System Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- Internet connection for AI processing
- 4GB RAM minimum (8GB recommended)

## Installation Steps

### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

### 2. Download Project Files
Download all project files to a folder on your computer:
- app.py
- universal_data_handler.py
- query_generator.py
- response_formatter.py
- privacy_policy.py
- requirements_local.txt
- .streamlit/config.toml

### 3. Open Command Prompt/Terminal
- **Windows**: Press `Windows + R`, type `cmd`, press Enter
- **macOS/Linux**: Open Terminal application

### 4. Navigate to Project Folder
```bash
cd path/to/your/project/folder
```

### 5. Create Virtual Environment (Recommended)
```bash
python -m venv venv
```

### 6. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 7. Install Dependencies
```bash
pip install -r requirements_local.txt
```

### 8. Set Environment Variable (Optional)
Set your OpenRouter API key for AI features:

**Windows:**
```bash
set OPENROUTER_API_KEY=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
```

**macOS/Linux:**
```bash
export OPENROUTER_API_KEY=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
```

### 9. Run the Application
```bash
streamlit run app.py
```

## What Happens Next

1. The application will start and show a URL like `http://localhost:8501`
2. Your web browser will automatically open to the application
3. You can now upload data files and chat with your data
4. Press `Ctrl+C` in the command prompt to stop the application

## Troubleshooting

### Common Issues

**Python not found:**
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python`

**Permission errors:**
- Run command prompt as Administrator (Windows)
- Use `sudo` for installation commands (macOS/Linux)

**Module not found:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements_local.txt`

**Port already in use:**
- Use a different port: `streamlit run app.py --server.port 8502`

### Alternative Installation

If pip install fails, try installing packages individually:
```bash
pip install streamlit pandas requests psycopg2-binary mysql-connector-python pymongo
```

## Features Available Locally

- Upload CSV, JSON, SQL dump files
- Connect to local/remote databases
- AI-powered natural language queries
- Data visualization and analysis
- Privacy policy compliance
- All monetization features ready

## Local vs Cloud Differences

**Local Advantages:**
- No internet dependency for file processing
- Faster file uploads
- Complete privacy for sensitive data
- No usage limits

**Cloud Advantages:**
- No installation required
- Accessible from anywhere
- Automatic updates
- Better for sharing with others

## Sharing Your Local App

To share your locally running app:
1. Note your computer's IP address
2. Run with: `streamlit run app.py --server.address 0.0.0.0`
3. Others can access via `http://YOUR_IP:8501`
4. Make sure firewall allows connections

## Next Steps

Once running locally:
1. Test with your data files
2. Customize the interface if needed
3. Add your own API keys for production use
4. Deploy to cloud when ready for public access

Your Data Chatbot Agent is now ready to run on your local PC!