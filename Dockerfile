# Use Python official image
FROM python:3.12-slim

ARG VERSION_STR

# Set it as an environment variable so Python can see it
ENV VERSION_STR=$VERSION_STR
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Optional: Print it during build to verify
RUN echo "Building version: $VERSION_STR"

# Set work directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/America/Indiana/Indianapolis /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Copy project
COPY . /app/

RUN python3 manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Rebuild your image after these changes!
# Use the full path for the command
CMD ["gunicorn", "volunteer_tracker_app.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]