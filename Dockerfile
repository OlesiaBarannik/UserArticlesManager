# Use a slim version of Python 3.12 as the base image
FROM python:3.12-slim

# Install Poetry for dependency management
RUN pip install poetry

# Set the working directory inside the container
WORKDIR /app

# Copy pyproject.toml and poetry.lock to the container
COPY pyproject.toml poetry.lock /app/

# Install project dependencies using Poetry
RUN poetry install --no-root

# Copy the rest of the application files to the container
COPY . /app/

# Apply database migrations using Alembic
RUN poetry run alembic upgrade head

# Set the working directory again (redundant but safe for clarity)
WORKDIR /app

# Expose port 5000 for the application to run on
EXPOSE 5000

# Command to start the Flask application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000"]
