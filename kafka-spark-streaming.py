from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .master("spark://spark-master:7077") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Read stream from Kafka topic
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "new_topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Convert Kafka message to string
df_transformed = df.selectExpr("CAST(value AS STRING) as message")

# Print messages to console
query = df_transformed.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# query.awaitTermination()

df = df_transformed.drop("key")



# Write Stream to PostgreSQL
def write_to_postgres(df, epoch_id):
    df.write \
      .format("jdbc") \
      .option("url", "jdbc:postgresql://postgres:5432/kafka_streaming") \
      .option("dbtable", "kafka_messages") \
      .option("user", "postgres") \
      .option("password", "postgres") \
      .option("driver", "org.postgresql.Driver") \
      .mode("append") \
      .save()

df.writeStream \
    .foreachBatch(write_to_postgres) \
    .start() \
    .awaitTermination()
