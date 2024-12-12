ARG PYTHON_VERSION=3.12.5
FROM python:${PYTHON_VERSION}-slim AS builder

# Prevents Python from writing pyc files and from buffering stdout and stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

# Create a group for admin users
RUN groupadd -g 1001 AdminUsers

# Create an admin user and add to the group
RUN useradd -r -g AdminUsers admin && \
    chown admin:AdminUsers /app && \
    mkdir -p /home/admin/.nebulagraph/lite && \
    chown admin:AdminUsers /home/admin/.nebulagraph/lite

# Ensure the admin user has the necessary permissions
RUN chmod 755 /home/admin/.nebulagraph/lite

# Switch to the non-privileged user to run the application
USER admin

# Expose the port that the application listens on
EXPOSE 8000

# Run the application.
CMD ["uvicorn", "Server.Web_Server:app", "--host", "0.0.0.0", "--port", "8000"]
