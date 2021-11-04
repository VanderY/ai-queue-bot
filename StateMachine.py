from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup


class StateMachine(Helper):
    mode = HelperMode.snake_case

    REGISTRATION_STATE = ListItem()
    QUEUE_NUMBER_WAITING = ListItem()
    REWRITING_QUEUE_NUMBER = ListItem()


class UserStates(StatesGroup):
    viewing_queue = State()


if __name__ == '__main__':
    print(StateMachine.all())
