# Bedrock UI Chat

A Streamlit-based chat interface for Amazon Bedrock's Claude models.

## Features
- Chat with Claude 3.5 and 3.7 Sonnet models
- View Claude's thinking process (3.7 only)
- Persistent conversation history
- Secure authentication with rate limiting

## Getting Started

1. Install dependencies:
```bash
uv pip install -r requirements.txt
```

2. Configure authentication:
```bash
export ADMIN_USERNAME=your_username
export ADMIN_PASSWORD_HASH="$(python3 -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("your_password"))')"
```

3. Run the app:
```bash
streamlit run hello.py
```

Your chat history will be saved in `~/.bedrock-chat/threads/`.