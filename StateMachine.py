from aiogram.utils.helper import Helper, HelperMode, ListItem


class StateMachine(Helper):
    mode = HelperMode.snake_case

    REGISTRATION_STATE = ListItem()
    QUEUE_NUMBER_WAITING = ListItem()
    REWRITING_QUEUE_NUMBER = ListItem()


if __name__ == '__main__':
    print(StateMachine.all())
