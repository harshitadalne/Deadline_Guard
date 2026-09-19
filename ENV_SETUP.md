# Environment Setup Instructions

## Creating your .env file

The `.env` file is excluded from git for security reasons. You need to create it manually:

### Step 1: Copy the example file
```bash
cp .env.example .env
```

### Step 2: Edit the .env file

Open `.env` in your text editor and configure the following:

```env
# Database
DATABASE_URL=sqlite:///./deadline_guardian.db

# JWT Secret Key (Generate a secure random string)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration (Optional - AI features will work without this)
LLM_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-3.5-turbo
LLM_PROVIDER=openai

# Backend URL (for Streamlit to connect)
BACKEND_URL=http://localhost:8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Important Notes:

1. **SECRET_KEY**: Generate a secure random string. You can use Python:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **LLM_API_KEY**: This is optional. The application will work without AI features, but you won't be able to use:
   - Natural language task creation
   - AI-powered recommendations
   - Chat with Guardian
   
   To get an API key, visit: https://platform.openai.com/api-keys

3. **BACKEND_URL**: Keep as `http://localhost:8000` for local development.

### Quick Setup (Development)

For local development, you can use these minimal settings:

```env
DATABASE_URL=sqlite:///./deadline_guardian.db
SECRET_KEY=dev-secret-key-change-in-production
BACKEND_URL=http://localhost:8000
```

This will give you full functionality except AI features.
