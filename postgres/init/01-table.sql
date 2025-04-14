CREATE TABLE IF NOT EXISTS kafka_messages (
    id SERIAL PRIMARY KEY,
    message VARCHAR(255),
    timestamp TIMESTAMP
);