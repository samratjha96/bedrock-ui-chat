# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Lint and Format
Before committing changes, always run:
```bash
uvx ruff format
```

### Run the Application
```bash
# Set up authentication
export ADMIN_USERNAME=your_username
export ADMIN_PASSWORD_HASH="$(python3 -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("your_password"))')"

# Run the app
streamlit run hello.py
```

## Features

### Authentication
- Secure login with Argon2 password hashing
- Rate limiting: 3 attempts with 5-minute lockout

### Chat Interface
- Supports Claude 3.5 and 3.7 Sonnet models
- Thinking process display for Claude 3.7
- Conversation threading with history
- Sliding window context (15 messages) for API calls

### Storage
- Location: `~/.bedrock-chat/threads/`
- One JSON file per conversation
- Auto-save after each message
- Thread format:
```json
{
  "id": "thread_id",
  "created_at": "timestamp",
  "title": "First message...",
  "model": "model_id",
  "messages": [
    {
      "role": "user/assistant",
      "content": "message",
      "thinking": "reasoning (3.7 only)",
      "timestamp": "timestamp"
    }
  ]
}
```