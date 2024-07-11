FROM python:3.12-slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "asgi:main", "--host", "0.0.0.0", "--port", "5001"]

CMD ["python3", "main.py"]