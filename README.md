# Kafka-Spark-Postgres-Grafana Streaming Project

## Overview
This project is a real-time data streaming pipeline built using Kafka, Spark Structured Streaming, PostgreSQL, and Grafana. The goal is to ingest real-time data using a Kafka producer, process it using Spark Streaming, store it in PostgreSQL, and visualize the live data in Grafana.

## Architecture
1. Kafka Producer - Generates and sends real-time messages to Kafka.
2. Kafka & Zookeeper - Kafka acts as a message broker, and Zookeeper manages the Kafka cluster.
3. Spark Structured Streaming - Consumes messages from Kafka, processes them, and writes to PostgreSQL.
4. PostgreSQL - Stores the processed streaming data.
5. Grafana - Connects to PostgreSQL and visualizes the live data.

Data Flow: Kafka Producer → Kafka Topic → Spark Streaming → PostgreSQL → Grafana Dashboard

## Project Setup

### Prerequisites
Ensure you have Docker, Docker Compose, Git, and Python installed.

### Clone the Repository
git clone https://github.com/yourusername/kafka-spark-postgres-grafana-streaming.git  
cd kafka-spark-postgres-grafana-streaming  

### Start the Docker Containers
docker-compose up --build -d  

### Verify the Setup
docker ps  

## Project Components

### Kafka Producer
The producer generates real-time messages and sends them to Kafka.

Run the producer:  
docker exec -it kafka-producer python3 kafka_producer.py  

### Kafka & Zookeeper
Check Kafka Topics:  
docker exec -it kafka kafka-topics.sh --list --bootstrap-server kafka:9092  

Consume Kafka Messages:  
docker exec -it kafka kafka-console-consumer.sh --topic new_topic --bootstrap-server kafka:9092 --from-beginning  

### Spark Structured Streaming
Run the Spark Job:  
Before running below command run this command :
docker cp kakfa-spark-streaming.py spark-master:/opt/bitnami/spark/ # so that it will copy this python file to spakr-master container at /opt/bitnami/spark/ location, then below command will run
docker exec -it spark-master spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/bitnami/spark/kafka-spark-streaming.py  

### PostgreSQL
Connect to the Database:  
docker exec -it postgres psql -U postgres -d kafka_streaming  

Check Data in Table:  
SELECT * FROM kafka_messages;  

### Grafana
1. Open Grafana: http://localhost:3000  
   - Username: admin  
   - Password: admin  

2. Add a PostgreSQL Data Source:  
   - URL: postgres:5432  
   - Database: kafka_streaming  
   - User: postgres  
   - Password: password  

3. Create a Dashboard:  
   - Select Panel Type: Time Series  
   - Query: SELECT timestamp, message FROM kafka_messages ORDER BY timestamp DESC  
   - Click Save → Apply  

## Stopping the Services
docker-compose down  

## Next Steps
- Deploy on the Cloud  
- Enhance the Kafka Producer with real-world data  
- Add Alerting in Grafana  

## Contributing
Fork this repository, create a pull request, or suggest improvements.

## License
MIT License
