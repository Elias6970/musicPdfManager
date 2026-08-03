FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY __init__.py .
COPY main.py .
COPY tests tests
COPY api api
COPY app app

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
