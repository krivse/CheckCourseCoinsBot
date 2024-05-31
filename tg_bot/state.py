from dataclasses import dataclass, field
from typing import Dict

from aiogram.fsm.state import StatesGroup, State


class BaseState(StatesGroup):
    """State for setting all specified pairs."""
    symbol = State()
    price = State()
    min = State()
    max = State()


@dataclass
class TemporaryStorage(StatesGroup):
    """Temporary storage for all specified pairs."""
    data: Dict = field(default_factory=dict)

    def update_data(self, symbol, min_p, max_p):
        """Adding new pair to the temporary storage."""
        return self.data.update({symbol: {'min': min_p, 'max': max_p}})

    @property
    def get_data(self):
        """Getting all pairs from the temporary storage."""
        return self.data

    def del_data(self, key):
        """Deleting pair from the temporary storage."""
        data = self.get_data
        del data[key]


ts = TemporaryStorage()
