from aiogram.utils.helper import Helper, HelperMode, ListItem


class StateMachine(Helper):
    mode = HelperMode.snake_case

    QUEUE_NUMBER_WAITING = ListItem()
    QUEUE_NUMBER_RECEIVED = ListItem()


if __name__ == '__main__':
    print(StateMachine.all())
