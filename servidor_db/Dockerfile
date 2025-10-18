FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY servidor_db.py .
CMD ["python", "servidor_db.py"]