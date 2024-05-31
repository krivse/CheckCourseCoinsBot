from aiogram import F, Dispatcher

import asyncio
from os import getenv
from aiogram import html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tg_bot.coinmarketcup import get_price
from tg_bot.keyboards import base_markup, del_pairs_markup
from tg_bot.state import BaseState, ts


async def start(message: Message) -> None:
    """Starting the bot

    :arg message: Message update."""
    await message.answer(
        f'Hello {html.bold(message.from_user.full_name)}, \n'
        f'set or delete the pair for checking',
        reply_markup=base_markup)


async def select_action(call: CallbackQuery, state: FSMContext) -> None:
    """Setting or deleting the pair for checking

    :arg call: CallbackQuery update
    :arg state: FSMContext state."""
    if call.data == 'set_pair':
        await call.message.edit_text('Enter the name of the coin for checking')
        await state.set_state(BaseState.symbol.state)
    elif call.data == 'del_pair':
        await call.message.edit_text(
            'Enter the name of the coin for deleting',
            reply_markup=await del_pairs_markup())


async def del_pair(call: CallbackQuery, state: FSMContext) -> None:
    """Deleting the pair from the temporary storage and deleting the message
    or canceling the process

    :arg call: CallbackQuery update
    :arg state: FSMContext state."""
    symbol = call.data[4:]
    if symbol == 'cancel':
        await call.message.edit_text('Cancelled')
        return
    ts.del_data(symbol)
    await call.message.edit_text(f'{symbol} deleted')
    await state.clear()


async def state_symbol(message: Message, state: FSMContext) -> None:
    """Setting the symbol of the coin

    :arg message: Message update
    :arg state: FSMContext state."""
    try:
        symbol = message.text.strip().upper()
        # Getting the price of the coin and displaying it
        price = await get_price(symbol)
        await message.answer(f'{symbol} price: {round(price, 2)}')
        await message.answer('Enter min price for checking')
        await state.update_data(symbol=symbol, price=price)
        await state.set_state(BaseState.min)
    except IndexError:
        await message.answer(
            'The pair is not found, try again and enter the name of the coin to check!\n'
            'Enter only the name of the coin, not the number')


async def state_min_value(message: Message, state: FSMContext) -> None:
    """Setting the minimum value of price

    :arg message: Message update
    :arg state: FSMContext state."""
    try:
        min_p = float(message.text.strip())
        price = (await state.get_data()).get('price')
        # Checking the minimum value of price
        if float(min_p) < price / 100 * 0.001 or float(min_p) > price - (price * 0.001 / 100):
            await message.answer('Minimum price must be more or less than 0.1% of the current price')
        else:
            await state.update_data(min=message.text.strip())
            await message.answer('Enter max price for checking')
            await state.set_state(BaseState.max)
    except ValueError:
        await message.answer('Enter only numbers')


async def state_max_value(message: Message, state: FSMContext) -> None:
    """Setting the maximum value of price
    Checking the maximum and minimum value of price from coinmarketcap

    :arg message: Message update
    :arg state: FSMContext state."""
    max_p = message.text.strip()
    data = await state.get_data()
    old_price = data.get('price')
    try:
        # Checking the maximum and minimum value of price
        if float(max_p) < old_price + (old_price * 0.001 / 100):
            await message.answer('Maximum price must be more of the current price')
            return
    except ValueError:
        await message.answer('Enter only numbers')
        return

    # Outputting the current price of the pair and the range of values
    symbol = data.get('symbol')
    min_p = data.get('min')
    await message.answer(f'{symbol} current price {old_price}:\n'
                         f'set the range {min_p} - {max_p} USD ')
    await state.clear()
    # Updating the temporary storage with the new values
    ts.update_data(
        symbol=symbol,
        min_p=min_p,
        max_p=max_p
    )
    while True:
        for symbol, values in ts.get_data.items():
            # Checking the price of the pair from api coinmarketcap
            price = await get_price(symbol)
            # Checking the values of the pair from the temporary storage
            if any([price <= float(values.get('min')), price >= float(values.get('max'))]):
                await message.answer(f'{symbol} price: {price}, quote: {round(price - old_price), 2}')
                ts.del_data(symbol)
        # Waiting for the next cycle in seconds for the checking the price
        await asyncio.sleep(int(getenv('SECONDS')))


def register_handlers(dp: Dispatcher):
    dp.message.register(start, CommandStart())
    dp.callback_query.register(select_action, F.data.in_(['set_pair', 'del_pair']))
    dp.callback_query.register(del_pair, F.data.startswith('del_'))
    dp.message.register(state_symbol, BaseState.symbol)
    dp.message.register(state_min_value, BaseState.min)
    dp.message.register(state_max_value, BaseState.max)