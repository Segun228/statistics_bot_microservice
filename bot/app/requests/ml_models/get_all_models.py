import aiohttp
import asyncio
import os
import json
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



async def retrieve_model(telegram_id, model_id=None):
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
        exact_url = f"{base_url}ml-algorithms/model/{f'{model_id}/' if model_id else ''}" 
        logging.debug(f"Sending to {exact_url}")

        async with session.get(
            exact_url, 
            headers=headers,
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("датасеты получены")
                return await response.json()
            else:
                return None


async def post_model(
    telegram_id, 
    csv_buffer,
    name,
    description,
    target,
    features,
    task,
    type
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")

    if not base_url:
        logging.error("No base URL was provided")
        raise ValueError("No base URL was provided")
    if not telegram_id:
        logging.error("No base telegram_id was provided")
        raise ValueError("No telegram_id was provided")
    if csv_buffer is None:
        raise ValueError("CSV buffer is empty")

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bot {telegram_id}",
        }

        exact_url = f"{base_url}ml-algorithms/model-create/"
        logging.debug(f"Sending to {exact_url}")

        form = aiohttp.FormData()
        form.add_field("name", name)
        form.add_field("description", description)
        form.add_field("task", task)
        form.add_field("type", type)
        form.add_field("target", target)
        form.add_field("features", json.dumps(features))
        csv_buffer.seek(0)
        form.add_field(
            "file",
            csv_buffer,
            filename=f"{name}.csv",
            content_type="text/csv"
        )

        async with session.post(
            exact_url,
            headers=headers,
            data=form
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Датасет отправлен")
                return await response.read()
            else:
                text = await response.text()
                logging.error(f"Ошибка {response.status}: {text}")
                return None


async def delete_model(telegram_id, model_id):
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
        exact_url = f"{base_url}ml-algorithms/model/{f'{model_id}/' if model_id else ''}" 
        logging.debug(f"Sending to {exact_url}")

        async with session.delete(
            exact_url, 
            headers=headers,
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("датасеты получены")
                return await response.json()
            else:
                return None