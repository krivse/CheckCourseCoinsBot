from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.state import ts

# Creating markup for adding and deleting pairs
base_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f'Add pair', callback_data='set_pair')],
        [InlineKeyboardButton(text=f'Delete pair', callback_data='del_pair')]]
)


async def del_pairs_markup():
    """Creating markup for deleting pairs"""
    markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    for symbol, values in ts.get_data.items():
        markup.inline_keyboard.append([InlineKeyboardButton(
            text=symbol, callback_data=f'del_{symbol}')])
    markup.inline_keyboard.append([InlineKeyboardButton(
        text='Cancel', callback_data='del_cancel')])
    return markup
