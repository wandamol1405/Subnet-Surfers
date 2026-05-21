FROM python:3.12-slim

WORKDIR /app

RUN pip install cryptography

COPY server.py .

EXPOSE 5000

CMD ["python", "-u", "server.py"]