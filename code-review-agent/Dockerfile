FROM python:3.11-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copy and install Python dependencies first (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the project
COPY backend/ ./backend/
COPY .env .env

# create data directory for SQLite
RUN mkdir -p data

# expose port
EXPOSE 8000

# run the app
CMD ["python", "-m", "backend.main"]