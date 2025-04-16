FROM python:3.10
RUN pip install kafka-python faker
COPY kafka_producer.py .
CMD ["python", "kafka_producer.py"]
