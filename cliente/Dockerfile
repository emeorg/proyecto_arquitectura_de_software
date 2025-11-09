FROM python:3.10-slim
WORKDIR /app
COPY cliente.py .
RUN pip install --no-cache-dir rich
CMD ["tail", "-f", "/dev/null"]