FROM python:3.13-alpine

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "src.celery_app", "worker", "--loglevel=info"]