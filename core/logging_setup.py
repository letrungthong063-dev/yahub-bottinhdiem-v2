"""Thiết lập logging màu cho console. Gọi setup_logging() một lần duy nhất trong bot.py."""

import logging


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG":    "\033[37m",
        "INFO":     "\033[36m",
        "WARNING":  "\033[33m",
        "ERROR":    "\033[31m",
        "CRITICAL": "\033[35m",
    }
    TAGS = {
        "[BXH]":      "\033[32m",
        "[ENABLE]":   "\033[32m",
        "[DISABLE]":  "\033[31m",
        "[GRANT]":    "\033[32m",
        "[REVOKE]":   "\033[31m",
        "[COOLDOWN]": "\033[33m",
        "[PUBLIC]":   "\033[32m",
        "[PRIVATE]":  "\033[31m",
    }
    RESET = "\033[0m"
    GRAY  = "\033[90m"
    BOLD  = "\033[1m"

    def format(self, record):
        time_str    = f"{self.GRAY}{self.formatTime(record, '%d/%m/%Y %H:%M:%S')}{self.RESET}"
        level_color = self.COLORS.get(record.levelname, self.RESET)
        level_str   = f"{level_color}{self.BOLD}[{record.levelname}]{self.RESET}"
        msg = record.getMessage()
        for tag, color in self.TAGS.items():
            if msg.startswith(tag):
                msg = f"{color}{self.BOLD}{tag}{self.RESET} {msg[len(tag)+1:]}"
                break
        return f"{time_str} {level_str} {msg}"


def setup_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    logging.root.handlers = []
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    return logging.getLogger("yahub-bot")
