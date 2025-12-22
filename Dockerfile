# Use Python official image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Add the local bin to the PATH just in case
ENV PATH="/home/app/.local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Rebuild your image after these changes!
# Use the full path for the command
CMD ["gunicorn", "volunteer_tracker_app.wsgi:application", "--bind", "0.0.0.0:8000"]