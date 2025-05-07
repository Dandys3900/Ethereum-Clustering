###################################
# @file Dockerfile
# @author Tomáš Daniel (xdanie14)
# @brief File generating application Docker image.
###################################

ARG PYTHON_VERSION=3.12.5
FROM python:${PYTHON_VERSION}-slim AS builder

# Prevents Python from writing pyc files and from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy rest of application
COPY . .

# Create group for admin users
RUN groupadd -g 1001 AdminUsers

# Create admin user and add it to group
RUN useradd -r -g AdminUsers admin && \
    chown admin:AdminUsers /app

# Switch to non-privileged user to run application
USER admin

# Ensure Python can see modules from project folder(s)
ENV PYTHONPATH=/app
