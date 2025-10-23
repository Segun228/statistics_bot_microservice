import aiohttp
import asyncio
import os
import logging
from dotenv import load_dotenv
from pprint import pprint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

async def get_all_models(telegram_id, model_task=None, model_type = None):
    load_dotenv()
    base_url = os.getenv("BASE_URL")

    if not base_url:
        logging.error("No base URL was provided")
        raise ValueError("No base URL was provided")
    if not telegram_id:
        logging.error("No base telegram_id was provided")
        raise ValueError("No telegram_id was provided")
        
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bot {telegram_id}",
        }
        data = {
            "type":model_type,
            "task":model_task
        }
        exact_url = f"{base_url}ml-algorithms/get_models" 
        logging.debug(f"Sending to {exact_url}")

        async with session.get(
            exact_url, 
            headers=headers,
            data=data
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("датасеты получены")
                return await response.json()
            else:
                return None
