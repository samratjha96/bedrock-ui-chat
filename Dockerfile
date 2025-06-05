FROM python:3.11-slim

# Install uv and set up environment
RUN pip install --no-cache-dir uv argon2-cffi
ENV PYTHONPATH=/app

# Set up admin credentials
ARG ADMIN_PASSWORD
RUN python3 -c "from argon2 import PasswordHasher; import os; password_hash = PasswordHasher().hash(os.environ.get('ADMIN_PASSWORD', 'default')); print(f'ENV ADMIN_PASSWORD_HASH={password_hash}')" > /tmp/env && \
    cat /tmp/env >> /etc/environment && \
    rm /tmp/env

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