FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask requests

EXPOSE 80

CMD ["python", "app.py"]
