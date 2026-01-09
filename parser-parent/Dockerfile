FROM python:3.11-slim
WORKDIR /app

# Install system dependencies required for psycopg2 and document processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv - fast Python package installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies using uv (much faster than pip)
RUN uv pip install --system --no-cache -r requirements.txt
# Copy application code
COPY parser/ .
# Create uploads directory
RUN mkdir -p uploads
# Expose port
EXPOSE 7312
# Run the application
CMD ["python", "app.py"]
