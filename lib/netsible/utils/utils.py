import os
import time

import ping3
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
            print(Fore.GREEN + "SUCCESS: %0.5f: \n%s" % (time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "SUCCESS: %0.5f [%s]: \n%s" % (time.time(), host, msg) + Style.RESET_ALL)


def ping_ip(client_info, only_ip=False):
    host = client_info['host'] if not only_ip else client_info
    result = ping3.ping(host)

    if result is False or result is None:
        Display.warning("Can't connect to the target.")
        return

    Display.success(f"Ping successful. Round-trip time: {result} ms")
