
FROM python:3.10-slim

WORKDIR /app

COPY . /app

EXPOSE 8085

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
