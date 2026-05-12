FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p backend/ 

COPY __init__.py backend/
COPY main.py backend/
COPY tests backend/tests
COPY api backend/api
COPY app backend/app

CMD ["fastapi", "dev", "backend/main.py", "--host", "0.0.0.0", "--port", "8000"]
