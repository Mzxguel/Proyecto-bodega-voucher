import threading
import time


class ScannerHandler:
    def __init__(self, callback_on_scan):
        """callback_on_scan(codigo_str)
        callback que recibe el código escaneado (str).
        """
        self.callback = callback_on_scan