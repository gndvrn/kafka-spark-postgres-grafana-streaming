from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkStreamingTransactions") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.postgresql:postgresql:42.5.0") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/postgresql-42.5.0.jar") \
    .config("spark.sql.shuffle.partitions", "1") \
    .getOrCreate()

# Схема JSON-сообщений о транзакциях из Kafka
transaction_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("branch_id", IntegerType(), False),
    StructField("transaction_time", TimestampType(), False),
    StructField("amount", DoubleType(), False),
    StructField("payment_method", StringType(), False),
    StructField("customer_id", StringType(), True),
    StructField("items_count", IntegerType(), False),
    StructField("is_return", BooleanType(), False),
    StructField("operator_id", StringType(), False),
    StructField("additional_info", MapType(StringType(), StringType()), False)
])

# Чтение данных из Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "transactions") \
    .option("startingOffsets", "earliest") \
    .load()

# Парсинг JSON и преобразование в структурированный DataFrame
parsed_df = df.select(
    from_json(col("value").cast("string"), transaction_schema).alias("data")) \
    .select("data.*") \
    .withColumn("transaction_time", to_timestamp(col("transaction_time"))) \
    .withColumn("additional_info", to_json(col("additional_info")))

# Функция для записи в PostgreSQL
def write_transactions_to_postgres(batch_df, batch_id):
    processed_df = batch_df.select(
        "transaction_id",
        "branch_id",
        "transaction_time",
        "amount",
        "payment_method",
        "customer_id",
        "items_count",
        "is_return",
        "operator_id",
        "additional_info"
    )
    
    processed_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/offline-store-transactions") \
        .option("dbtable", "transactions") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# Дополнительная обработка: агрегация по филиалам
def aggregate_branch_stats(batch_df, batch_id):
    branch_stats = batch_df.groupBy("branch_id") \
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            sum(when(col("is_return"), 1).otherwise(0)).alias("return_count")
        )
    
    branch_stats.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/offline-store-transactions") \
        .option("dbtable", "branch_stats_realtime") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

# Объединенная функция обработки
def process_and_write_batch(batch_df, batch_id):
    write_transactions_to_postgres(batch_df, batch_id)
    aggregate_branch_stats(batch_df, batch_id)

# Запуск стриминга с записью в PostgreSQL
query = parsed_df.writeStream \
    .foreachBatch(process_and_write_batch) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/transactions") \
    .start()

query.awaitTermination()