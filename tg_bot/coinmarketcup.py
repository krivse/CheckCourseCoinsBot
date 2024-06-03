import os

import coinmarketcapapi
from dotenv import load_dotenv

load_dotenv()

cmc_client = coinmarketcapapi.CoinMarketCapAPI(os.getenv('CMC_KEY'))


async def get_price(symbol: str) -> float:
    """Getting the price of the coin

    :arg symbol: Symbol of the coin
    :return: Price of the coin"""
    result = cmc_client.cryptocurrency_quotes_latest(symbol=symbol, convert='USD')
    price = result.data.get(symbol)[0].get('quote').get('USD').get('price')
    return price
