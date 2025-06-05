FROM python:3.11-slim

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy requirements files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV ADMIN_USERNAME=""
ENV ADMIN_PASSWORD_HASH=""

# Create directory for chat history
RUN mkdir -p /root/.bedrock-chat/threads

# Volume for chat history
VOLUME /root/.bedrock-chat/threads

# Run the application
CMD ["uv", "run", "streamlit", "run", "bedrock.py"]