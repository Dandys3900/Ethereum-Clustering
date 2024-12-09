ARG PYTHON_VERSION=3.12.5
FROM python:${PYTHON_VERSION}-slim as builder

# Prevents Python from writing pyc files and from buffering stdout and stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

# Create a non-privileged user that the app will run under.
RUN groupadd -g 1000 NonPrivUsers && \
    useradd -r -g NonPrivUsers executor && \
    chown executor:NonPrivUsers /app

# Switch to the non-privileged user to run the application
USER executor

# Expose the port that the application listens on
EXPOSE 8000

# Run the application.
CMD fastapi dev Server/Web_Server.py
