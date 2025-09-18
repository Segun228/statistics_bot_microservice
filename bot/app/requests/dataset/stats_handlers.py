import aiohttp
import asyncio
import os
import logging
from dotenv import load_dotenv
from pprint import pprint
from io import BytesIO


async def count_n(
    telegram_id,
    id,
    mde = 5
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")

    if not base_url:
        logging.error("No base URL was provided")
        raise ValueError("No base URL was provided")
    if not telegram_id or not id:
        logging.error("No base telegram_id was provided")
        raise ValueError("No telegram_id was provided")
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bot {telegram_id}",
        }

        exact_url = f"{base_url}ab-tests/sample-size/{id}/"
        logging.debug(f"Sending to {exact_url}")

        data = {
            "mde":mde
        }
        async with session.post(
            exact_url,
            headers=headers,
            json=data
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Результат получен")
                return await response.json()
            else:
                text = await response.text()
                logging.error(f"Ошибка {response.status}: {text}")
                return None


async def count_mde(
    telegram_id,
    id,
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")

    if not base_url:
        logging.error("No base URL was provided")
        raise ValueError("No base URL was provided")
    if not telegram_id or not id:
        logging.error("No base telegram_id was provided")
        raise ValueError("No telegram_id was provided")
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bot {telegram_id}",
        }

        exact_url = f"{base_url}ab-tests/mde/{id}/"
        logging.debug(f"Sending to {exact_url}")

        async with session.post(
            exact_url,
            headers=headers,
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Результат получен")
                return await response.json()
            else:
                text = await response.text()
                logging.error(f"Ошибка {response.status}: {text}")
                return None


async def z_test(
    telegram_id,
    id,
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")

    if not base_url:
        logging.error("No base URL was provided")
        raise ValueError("No base URL was provided")
    if not telegram_id or not id:
        logging.error("No base telegram_id was provided")
        raise ValueError("No telegram_id was provided")
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bot {telegram_id}",
        }

        exact_url = f"{base_url}ab-tests/z-test/{id}/"
        logging.debug(f"Sending to {exact_url}")

        async with session.post(
            exact_url,
            headers=headers,
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Результат получен")
                return await response.json()
            else:
                text = await response.text()
                logging.error(f"Ошибка {response.status}: {text}")
                return None