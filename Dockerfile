FROM python:3.12-slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-k", "eventlet", "--bind", "0.0.0.0:5000", "wsgi:app"]
