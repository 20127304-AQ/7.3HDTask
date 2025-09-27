FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

# Use gunicorn to run the flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
