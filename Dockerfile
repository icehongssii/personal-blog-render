# Use the base image with Python 3.10
FROM tiangolo/uvicorn-gunicorn:python3.10-slim

# Set the maintainer label
LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"


ENV REDIS_HOST=${REDIS_HOST}
ENV REDIS_PWD=${REDIS_PWD}

# Set the working directory to /app
WORKDIR /app

# Copy the Poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Disable the creation of virtual environments by Poetry
# and install the dependencies globally
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the main application to the container
COPY ./api /app/api
COPY ./static /app/static
COPY ./templates /app/templates

# You can configure the startup command in the CMD directive if needed
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "80"]


# If app.py is not using FastAPI and needs to be run differently,
# adjust the CMD directive accordingly, e.g., for a Flask app:
# CMD ["python", "app.py"]
