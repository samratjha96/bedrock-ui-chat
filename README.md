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
uv sync
```

2. Configure authentication:
```bash
export ADMIN_USERNAME=your_username
export ADMIN_PASSWORD_HASH="$(python3 -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("your_password"))')"
```

3. Run the app:
```bash
uv run streamlit run bedrock.py
```

Your chat history will be saved in `~/.bedrock-chat/threads/`.

## Docker

1. Build the image:
```bash
docker build -t bedrock-chat .
```

2. Run the container:
```bash
docker run -p 8501:8501 \
  -v ~/.bedrock-chat/threads:/root/.bedrock-chat/threads \
  -e ADMIN_USERNAME=your_username \
  -e ADMIN_PASSWORD_HASH="$(python3 -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("your_password"))')" \
  bedrock-chat
```
