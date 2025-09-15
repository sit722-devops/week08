# week08/backend/product_service/Dockerfile

FROM python:3.10

# Set working directory inside the container
WORKDIR /code

# Copy dependency list first (better build cache)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the actual application code
COPY app /code/app

# Product service runs on port 8000
EXPOSE 8000

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
