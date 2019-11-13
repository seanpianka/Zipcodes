import logging
import sys


class CustomFormatter(logging.Formatter):
    err_fmt = "[*] ERROR: %(msg)s"
    dbg_fmt = "[-] DEBUG: %(module)s: %(lineno)d: %(msg)s"
    info_fmt = "[+] %(msg)s"

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style="%")

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = CustomFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._style._fmt = CustomFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._style._fmt = CustomFormatter.err_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class CustomLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super(CustomLogger, self).__init__(*args, **kwargs)

        handler = logging.StreamHandler(sys.stdout)
        if sys.version_info >= (3, 0):
            formatter = CustomFormatter()
            handler.setFormatter(formatter)
        self.addHandler(handler)

        self.setLevel(logging.INFO)
