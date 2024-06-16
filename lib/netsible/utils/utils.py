import os
import time
from colorama import Fore, Style


class Display:
    @staticmethod
    def debug(msg: str, host: str | None = None) -> None:
        if host is None:
            print("LOG: %6d %0.5f: %s" % (os.getpid(), time.time(), msg))
        else:
            print("LOG: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg))

    @staticmethod
    def warning(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.YELLOW + "WARNING: %6d %0.5f: %s" % (os.getpid(), time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "WARNING: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg) + Style.RESET_ALL)

    @staticmethod
    def error(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.RED + "ERROR: %6d %0.5f: %s" % (os.getpid(), time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.RED + "ERROR: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg) + Style.RESET_ALL)

    @staticmethod
    def success(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.GREEN + "SUCCESS: %0.5f: %s" % (time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "SUCCESS: %0.5f [%s]: %s" % (time.time(), host, msg) + Style.RESET_ALL)

