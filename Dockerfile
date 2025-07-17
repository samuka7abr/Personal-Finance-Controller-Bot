FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs config

ENV MPLBACKEND=Agg
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "main.py"] 