from django.apps import AppConfig
import logging

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "backend"

    def ready(self):
        from signals import signals
        try:
            from kafka_broker.utils import ensure_topic_exists
            ensure_topic_exists()
        except Exception as e:
            logging.warning(f"Kafka topic creation skipped: {e}")