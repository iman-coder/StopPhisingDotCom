FROM python:3.11-slim

WORKDIR /app

# Prevents Python from writing .pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime utilities (curl for healthchecks) and tini as PID 1
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl tini \
	&& rm -rf /var/lib/apt/lists/*

# Install build deps (if needed) then dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

EXPOSE 8000

# Run the app with uvicorn
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
