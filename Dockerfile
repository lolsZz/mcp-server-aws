# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
# Use an official Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install build system and dependencies
RUN pip install --upgrade pip && \
    pip install hatchling

# Copy the project files into the container
COPY . /app

# Install the project in editable mode (if necessary)
RUN hatch build && pip install .

# Set up environment variables for AWS credentials
ENV AWS_ACCESS_KEY_ID=your_access_key_id
ENV AWS_SECRET_ACCESS_KEY=your_secret_access_key
ENV AWS_REGION=us-east-1

# Run the MCP server
CMD ["hatch", "run", "mcp-server-aws"]
