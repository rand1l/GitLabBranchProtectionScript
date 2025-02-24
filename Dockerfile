# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install the 'requests' library directly
RUN pip install --no-cache-dir requests

# Copy all project files into the container
COPY . .

# Execute the GitLab Branch Protector script
CMD ["python", "protect_branches.py"]
