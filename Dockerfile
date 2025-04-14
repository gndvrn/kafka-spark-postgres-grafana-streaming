FROM python:3.10
RUN pip install kafka-python
COPY kafka_producer.py .
CMD ["python", "kafka_producer.py"]
