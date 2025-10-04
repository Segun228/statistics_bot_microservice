from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
import json
import logging
import uuid
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

KAFKA_BROKER_DOCKER = os.getenv("KAFKA_BROKER_DOCKER")
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
PRODUCER_CLIENT_ID = os.getenv("PRODUCER_CLIENT_ID")
LOGS = os.getenv("LOGS", "false").lower() == "true"

if not KAFKA_BROKER_DOCKER:
    raise RuntimeError("KAFKA_BROKER_DOCKER not set in environment")

_producer = None

async def ensure_topic_exists():
    if not LOGS:
        logging.warning("The logging mode is turned off")
        return
    
    try:
        if not KAFKA_BROKER_DOCKER:
            raise RuntimeError("KAFKA_BROKER_DOCKER not set in environment")
        admin_client = AIOKafkaAdminClient(
            bootstrap_servers=KAFKA_BROKER_DOCKER,
            client_id="admin_client"
        )
        
        await admin_client.start()
        
        topic_list = [NewTopic(
            name=KAFKA_TOPIC,
            num_partitions=1,
            replication_factor=1
        )]

        try:
            await admin_client.create_topics(new_topics=topic_list)
            print(f"Topic '{KAFKA_TOPIC}' created")
        except Exception as e:
            if "TopicAlreadyExistsError" in str(e) or "already exists" in str(e):
                print(f"Topic '{KAFKA_TOPIC}' already exists")
            else:
                raise e
                
    except Exception as e:
        logging.error(f"Failed to create topic: {e}")
    finally:
        await admin_client.close()

async def get_producer():
    global _producer
    if not LOGS:
        return None
    if not KAFKA_BROKER_DOCKER:
        raise RuntimeError("KAFKA_BROKER_DOCKER not set in environment")
    if _producer is None:
        try:
            _producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BROKER_DOCKER,
                client_id=PRODUCER_CLIENT_ID,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await _producer.start()
        except Exception as e:
            logging.error(f"Kafka producer not available: {e}")
            _producer = None
    return _producer

async def build_log_message(
    telegram_id,
    action,
    source,
    payload=None,
    platform="bot",
    level="INFO",
    env="prod",
    timestamp=None
):
    if not LOGS:
        return {"status": "skipped", "reason": "logging_disabled"}
    
    message = {
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "trace_id": str(uuid.uuid4()),
        "telegram_id": telegram_id,
        "platform": platform,
        "action": action,
        "level": level,
        "event_type": action,
        "source": source,
        "env": env,
        "message": f"User {telegram_id} performed {action}",
        "payload": payload
    }
    
    return await send_to_kafka(message)

async def send_to_kafka(data):
    if not LOGS:
        return {"status": "skipped", "reason": "logging_disabled"}
        
    producer = await get_producer()
    if producer is None:
        logging.info(f"Kafka not available, skipping log: {data}")
        return {"status": "skipped", "reason": "producer_unavailable"}

    try:
        messages = []
        
        if isinstance(data, list):
            for item in data:
                if hasattr(item, "dict"):
                    item = item.dict()
                messages.append(item)
                await producer.send_and_wait(KAFKA_TOPIC, value=item)
        else:
            if hasattr(data, "dict"):
                data = data.dict()
            messages.append(data)
            await producer.send_and_wait(KAFKA_TOPIC, value=data)

        result = {
            "status": "success",
            "messages_sent": len(messages),
            "sample": messages[0] if messages else None,
        }
        logging.info(f"Logged {len(messages)} messages to Kafka successfully!")
        return result

    except Exception as e:
        logging.error(f"Failed to send to Kafka: {e}")
        return {"status": "failed", "error": str(e)}

async def close_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None


def build_log_message_sync(
    telegram_id,
    action,
    source,
    payload=None,
    platform="bot",
    level="INFO",
    env="prod",
    timestamp=None
):
    if not LOGS:
        return {"status": "skipped", "reason": "logging_disabled"}
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        build_log_message(telegram_id, action, source, payload, platform, level, env, timestamp)
    )


async def init_kafka():
    if LOGS:
        await ensure_topic_exists()
        await get_producer()


async def async_init():
    await init_kafka()
