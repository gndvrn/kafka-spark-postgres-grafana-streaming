FROM bitnami/spark:3.3

# Установка curl и загрузка PostgreSQL JDBC драйвера
USER root
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -o /opt/bitnami/spark/jars/postgresql-42.5.0.jar \
    https://jdbc.postgresql.org/download/postgresql-42.5.0.jar

# Возвращаемся к пользователю spark
USER 1001

COPY kafka-spark-streaming.py /app/
WORKDIR /app

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.postgresql:postgresql:42.5.0", "kafka-spark-streaming.py"]