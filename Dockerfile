FROM python:3.9
WORKDIR /app
COPY kafka_producer.py .
RUN pip install confluent-kafka
CMD ["python3", "kafka_producer.py"]
