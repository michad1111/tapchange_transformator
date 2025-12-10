# Use Python 3.12 as base image
FROM python:3.12-slim

# TODO: WRITE DOCKERFILE

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Copy the application code
COPY . ./
RUN pip install --no-cache-dir -e .

# Run the application
CMD ["python", "-m", "studenttask.StudentTask"]
