import aiohttp
import asyncio
import os
import io
import logging
from dotenv import load_dotenv
from pprint import pprint
import pandas as pd
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

async def fit_model(
    telegram_id,
    model_id,
    df:pd.DataFrame
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    csv_buffer = io.BytesIO()
    df.to_csv(path_or_buf=csv_buffer)
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

        exact_url = f"{base_url}model-fit/{model_id}/"
        logging.debug(f"Sending to {exact_url}")

        form = aiohttp.FormData()
        csv_buffer.seek(0)
        form.add_field(
            "file",
            csv_buffer,
            filename="refit.csv",
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
                logging.error(text)

async def refit_model(
    telegram_id,
    model_id,
    df:pd.DataFrame
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    csv_buffer = io.BytesIO()
    df.to_csv(path_or_buf=csv_buffer)
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

        exact_url = f"{base_url}model-refit/{model_id}/"
        logging.debug(f"Sending to {exact_url}")

        form = aiohttp.FormData()
        csv_buffer.seek(0)
        form.add_field(
            "file",
            csv_buffer,
            filename="refit.csv",
            content_type="text/csv"
        )

        async with session.post(
            exact_url,
            headers=headers,
            data=form
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Датасет отправлен")
                return await response.json()
            else:
                text = await response.text()
                logging.error


async def predict_model(    
    telegram_id,
    model_id,
    df:pd.DataFrame
):
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    csv_buffer = io.BytesIO()
    df.to_csv(path_or_buf=csv_buffer)
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

        exact_url = f"{base_url}model-predict/{model_id}/"
        logging.debug(f"Sending to {exact_url}")

        form = aiohttp.FormData()
        csv_buffer.seek(0)
        form.add_field(
            "file",
            csv_buffer,
            filename="refit.csv",
            content_type="text/csv"
        )

        async with session.post(
            exact_url,
            headers=headers,
            data=form
        ) as response:
            if response.status in (200, 201, 202, 203):
                logging.info("Датасет отправлен")
                return await response.text()
            else:
                text = await response.text()
                logging.error(text)



