from fastapi import FastAPI
from contextlib import asynccontextmanager
from .clickhouse_client import insert_log_async
import asyncio
import os
import logging
from .kafka_consumer import KafkaLogConsumer
from .init_clickhouse import create_logs_table
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


KAFKA_BACKEND_TOPIC = os.getenv("KAFKA_BACKEND_TOPIC")


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_logs_table()
    logging.info("ClickHouse table ensured")


    backend_consumer = KafkaLogConsumer(KAFKA_BACKEND_TOPIC, insert_log_async)


    await backend_consumer.start()
    logging.info("Kafka consumers started")


    backend_task = asyncio.create_task(backend_consumer.consume_forever())
    logging.info("Kafka consumer tasks running")

    try:
        yield
    finally:
        logging.info("Shutting down Kafka consumers...")
        await backend_consumer.stop()
        backend_task.cancel()
        logging.info("Kafka consumers stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def ping():
    return {"status": "Kafka consumer is alive"}