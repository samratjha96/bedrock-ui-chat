FROM python:3.11-slim

# Install uv and set up environment
RUN pip install --no-cache-dir uv
ENV PYTHONPATH=/app

# Hash password on container start
ARG ADMIN_PASSWORD
RUN python3 -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("${ADMIN_PASSWORD}"))' > /tmp/password_hash
ENV ADMIN_PASSWORD_HASH=$(cat /tmp/password_hash)
RUN rm /tmp/password_hash

WORKDIR /app

# Copy requirements files and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync

# Copy application code
COPY . .

# Create chat history directory
RUN mkdir -p /root/.bedrock-chat/threads

# Volume for chat history
VOLUME /root/.bedrock-chat/threads

# Expose Streamlit port
EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "bedrock.py", "--server.address", "0.0.0.0"]