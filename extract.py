import os
import aiohttp
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Asynchronous function to fetch data for a single symbol
async def fetch_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={os.getenv('output_size')}&apikey={os.getenv('API_KEY')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Asynchronous function to fetch data for multiple symbols
async def fetch_all_data(symbols):
    return await asyncio.gather(*[fetch_data(symbol) for symbol in symbols])
print("Extraction successful")