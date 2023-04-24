import logging
import socket

from logging.handlers import SysLogHandler

logger = logging.getLogger()
logger.addHandler(SysLogHandler(address=('192.168.2.11', 516), facility=LOG_SYSLOG,socktype=socket.SOCK_DGRAM))

logger.info("Test bericht")


