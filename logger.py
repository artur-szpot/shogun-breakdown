"""
Provide easy-to-use, minimal typing required
overlay for using Colorama in CLI.
Designed with black command line background in mind.
"""
from enum import Enum
from typing import List

from colorama import Back
from colorama import Fore
from colorama import Style
from colorama import init


class MessageType(Enum):
    TEXT = 0
    INFO = 1
    SUCCESS = 2
    ERROR = 3
    WARN = 4
    HELP = 5
    CONTINUOUS = 100
    VARIABLE = 101


class LogType(Enum):
    DEBUG = 0
    DETAIL = 1
    SPLITS = 2


class Message:
    message_type: MessageType
    log_type: LogType
    text: str

    def __init__(self,
                 message_type: MessageType,
                 log_type: LogType,
                 text: str
                 ):
        self.message_type = message_type
        self.log_type = log_type
        self.text = text


class Logger:
    # Remember whether the newest message should begin from a new line or not.
    last_continuous: bool = False
    indent: int = 0
    queue: List[Message]
    log_levels: List[LogType]

    def __init__(self):
        """ Initialize the module. Required for Colorama. Called automatically. """
        init()
        self.log_levels = [LogType.DEBUG, LogType.DETAIL]
        # self.log_level = LogType.SPLITS
        self.queue = []

    def line(self) -> None:
        print()

    def nice_print(self, codes: List[MessageType], message: str) -> None:
        if MessageType.ERROR in codes:
            color = Back.RED + Fore.BLACK
        elif MessageType.WARN in codes:
            color = Back.YELLOW
            if MessageType.VARIABLE not in codes:
                color += Fore.BLACK
        elif MessageType.HELP in codes:
            color = Fore.YELLOW
        elif MessageType.INFO in codes:
            color = Back.CYAN + Fore.BLACK
        elif MessageType.SUCCESS in codes:
            color = Fore.GREEN
        else:
            color = ''

        if MessageType.VARIABLE in codes:
            color += Style.BRIGHT

        if not self.last_continuous:
            print(' ' * self.indent, end='')

        if MessageType.CONTINUOUS in codes:
            print(color + message + Style.RESET_ALL, end='')
            self.last_continuous = True
        else:
            print(color + message + Style.RESET_ALL)
            self.last_continuous = False

    def smart_print(self, codes: List[MessageType], message: str) -> None:
        """
        Provide shorthand for using the shorthand when
        interspersed with variables/highlighted values.
        """
        if MessageType.VARIABLE in codes:
            raise ValueError("Variables unsupported in smart_print!")
        highlighted = False
        msgs = message.split('%')
        for i in range(len(msgs)):
            msg_codes = codes
            msg_codes += MessageType.VARIABLE if highlighted else ''
            msg_codes += MessageType.CONTINUOUS if i < len(msgs) - 1 else ''
            self.nice_print(msg_codes, msgs[i])
            highlighted = not highlighted

    def print_message(self, message: Message):
        if message.log_type not in self.log_levels:
            return
        if message.message_type == MessageType.TEXT:
            print(message.text)
        elif message.message_type == MessageType.INFO:
            self.nice_print([MessageType.INFO], message.text)
        elif message.message_type == MessageType.WARN:
            self.nice_print([MessageType.WARN], message.text)
        elif message.message_type == MessageType.ERROR:
            self.nice_print([MessageType.ERROR], message.text)
        elif message.message_type == MessageType.SUCCESS:
            self.nice_print([MessageType.SUCCESS], message.text)

    def execute_queue(self):
        for message in self.queue:
            self.print_message(message)
        self.clear_queue()

    def clear_queue(self):
        self.queue = []

    def debug_text(self, message: str):
        self.print_message(Message(MessageType.TEXT, LogType.DEBUG, message))

    def queue_debug_text(self, message: str):
        self.queue.append(Message(MessageType.TEXT, LogType.DEBUG, message))

    def debug_info(self, message: str):
        self.print_message(Message(MessageType.INFO, LogType.DEBUG, message))

    def queue_debug_info(self, message: str):
        self.queue.append(Message(MessageType.INFO, LogType.DEBUG, message))

    def debug_warn(self, message: str):
        self.print_message(Message(MessageType.WARN, LogType.DEBUG, message))

    def queue_debug_warn(self, message: str):
        self.queue.append(Message(MessageType.WARN, LogType.DEBUG, message))

    def debug_error(self, message: str):
        self.print_message(Message(MessageType.ERROR, LogType.DEBUG, message))

    def queue_debug_error(self, message: str):
        self.queue.append(Message(MessageType.ERROR, LogType.DEBUG, message))

    def debug_success(self, message: str):
        self.print_message(Message(MessageType.SUCCESS, LogType.DEBUG, message))

    def queue_debug_success(self, message: str):
        self.queue.append(Message(MessageType.SUCCESS, LogType.DEBUG, message))

    def detail_text(self, message: str):
        self.print_message(Message(MessageType.TEXT, LogType.DETAIL, message))

    def queue_detail_text(self, message: str):
        self.queue.append(Message(MessageType.TEXT, LogType.DETAIL, message))

    def detail_info(self, message: str):
        self.print_message(Message(MessageType.INFO, LogType.DETAIL, message))

    def queue_detail_info(self, message: str):
        self.queue.append(Message(MessageType.INFO, LogType.DETAIL, message))

    def detail_error(self, message: str):
        self.print_message(Message(MessageType.ERROR, LogType.DETAIL, message))

    def queue_detail_error(self, message: str):
        self.queue.append(Message(MessageType.ERROR, LogType.DETAIL, message))

    def detail_success(self, message: str):
        self.print_message(Message(MessageType.SUCCESS, LogType.DETAIL, message))

    def queue_detail_success(self, message: str):
        self.queue.append(Message(MessageType.SUCCESS, LogType.DETAIL, message))

    def splits_text(self, message: str):
        self.print_message(Message(MessageType.TEXT, LogType.SPLITS, message))

    def queue_splits_text(self, message: str):
        self.queue.append(Message(MessageType.TEXT, LogType.SPLITS, message))

    def splits_info(self, message: str):
        self.print_message(Message(MessageType.INFO, LogType.SPLITS, message))

    def queue_splits_info(self, message: str):
        self.queue.append(Message(MessageType.INFO, LogType.SPLITS, message))

    def splits_error(self, message: str):
        self.print_message(Message(MessageType.ERROR, LogType.SPLITS, message))

    def queue_splits_error(self, message: str):
        self.queue.append(Message(MessageType.ERROR, LogType.SPLITS, message))

    def splits_success(self, message: str):
        self.print_message(Message(MessageType.SUCCESS, LogType.SPLITS, message))

    def queue_splits_success(self, message: str):
        self.queue.append(Message(MessageType.SUCCESS, LogType.SPLITS, message))


logger = Logger()
