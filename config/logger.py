import os
import logging
import colorlog
from logging.config import dictConfig

class InfoFilter(logging.Filter):
    def filter(self, record):
        # INFO and WARNING should be shown
        return record.levelno < logging.ERROR

class RemoveLevelFilter(object):
    def __init__(self, levelToSkip):
        self.level = levelToSkip

    def filter(self, record):
        return self.getLogLevelName(record.levelno) != self.level

    def getLogLevelName(self, levelno):
        switcher = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
            50: "CRITICAL"
        }
        return switcher.get(levelno, "INFO")

def configure_logger(config):

    # with open("logging.json", "r", encoding="utf-8") as fd:
    #     logging.config.dictConfig(json.load(fd))

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s :: %(levelname)s :: %(threadName)s :: %(module)s :: %(message)s",
            },
            "access": {
                "format": "%(message)s",
            },
            "color": {
                "()": "colorlog.LevelFormatter",
                "fmt": "%(log_color)s%(asctime)s :: %(levelname)s :: %(threadName)s :: %(module)s :: %(message)s",
            }
        },
        "filters": {
            "skipDebug": {
                "()": "config.logger.RemoveLevelFilter",
                "levelToSkip": "DEBUG"
            },
            "skipInfo": {
                "()": "config.logger.RemoveLevelFilter",
                "levelToSkip": "INFO",
            },
            "skipWarning": {
                "()": "config.logger.RemoveLevelFilter",
                "levelToSkip": "WARNING",
            },
            "skipError": {
                "()": "config.logger.RemoveLevelFilter",
                "levelToSkip": "ERROR",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "color",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": "app.log",
                "encoding": "utf8",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": "access.log",
                "filters": ["skipDebug", "skipWarning", "skipError"],
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "level": "ERROR",
                "filename": "error.log",
                "filters": ["skipDebug", "skipInfo"],
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
                "encoding": "utf8",
            }
        },
        "root": {
            "level": "DEBUG" if config["DEBUG"] else "INFO",
            "handlers": ["console", "file"] if config["DEBUG"] else ["console", "file", "access_file", "error_file"],
        }
    })
