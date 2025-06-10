FROM python:3.13

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

CMD ["sh", "-c", "cd resume && gunicorn --bind 0.0.0.0:8000 resume.wsgi"]