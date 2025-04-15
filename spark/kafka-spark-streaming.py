from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.postgresql:postgresql:42.5.0") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/postgresql-42.5.0.jar") \
    .config("spark.sql.shuffle.partitions", "1") \
    .getOrCreate()



# Схема JSON-сообщений из Kafka
schema = StructType([
    StructField("message", StringType(), True),
    StructField("processed_at", StringType(), True)
])

# Чтение данных из Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "new_topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Парсинг JSON и преобразование в структурированный DataFrame
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("processed_at", to_timestamp(col("processed_at")))

# Функция для записи в PostgreSQL
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/kafka_streaming") \
        .option("dbtable", "kafka_messages") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# Запуск стриминга с записью в PostgreSQL
query = parsed_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

query.awaitTermination()
