FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV FOLDER=/app/data
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["gunicorn", "web_server:app", "-b :8000"]
