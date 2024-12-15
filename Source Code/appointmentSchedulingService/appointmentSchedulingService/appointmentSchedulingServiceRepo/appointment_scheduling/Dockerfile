# Use Debian 12 as base image
FROM debian:12

# Create a non-root user and group
RUN groupadd -r myuser && useradd -r -g myuser myuser

# Set working directory
WORKDIR /appointmentScheduling_script

# Update package repository and install required packages
RUN apt-get update && apt-get install -y python3 python3-venv


# Copy application files
COPY requirements.txt requirements.txt
COPY appointmentScheduling_script /appointmentScheduling_script/

# Create and activate a Python virtual environment
RUN python3 -m venv venv
ENV PATH="/appointmentScheduling_script/venv/bin:$PATH"
ENV PYTHONUNBUFFERED 1

# Install dependencies within the virtual environment
# Upgrade pip to version 23.3
RUN pip install --upgrade pip==23.3
RUN pip install -r requirements.txt
RUN pip install gunicorn[gevent]

# Switch to non-root user
USER myuser

# Start the application using the virtual environment
CMD ["gunicorn", "-b", "0.0.0.0:3037", "--worker-class", "gevent", "--workers", "1", "app:app"]