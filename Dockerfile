# Stage 1: Build Python dependencies
FROM python:3.9 as builder

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Build Node.js dependencies and final image
FROM node:16.14.0

# Set the working directory inside the container
WORKDIR /app/backend

# Copy the Python dependencies from the previous stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Stage 2: Build Node.js dependencies and final image
FROM node:16.14.0

# Set the working directory inside the container
WORKDIR /app/frontend

# Copy the Python dependencies from the previous stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

COPY frontend/. .

# COPY frontend/package*.json ./
# COPY frontend/public/index.html /app/public/

WORKDIR /app

# Copy the rest of the application code to the container
COPY . .

WORKDIR /app/frontend
# Install JavaScript dependencies
RUN npm install

# Expose a port if your application requires it
EXPOSE 5001