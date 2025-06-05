FROM python:3.11-slim

# Install uv and set up environment
RUN pip install --no-cache-dir uv argon2-cffi
ENV PYTHONPATH=/app

# Set up admin credentials
ARG ADMIN_PASSWORD
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD:-default}

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
