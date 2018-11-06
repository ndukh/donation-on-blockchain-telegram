import json
import logging
import socket
from logging.handlers import SysLogHandler
from urllib import parse

import httplib2


class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True


# class to use papertrailapp
class MyLogger:
    def __init__(self, url, port):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        f = ContextFilter()
        self.logger.addFilter(f)
        syslog = SysLogHandler(address=(url, port))
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        syslog.setFormatter(formatter)
        self.logger.addHandler(syslog)

    def info(self, msg, *args):
        self.logger.info(msg, *args)

    def error(self, msg, *args):
        self.logger.error(msg, *args)

    def debug(self, msg, *args):
        self.logger.debug(msg, *args)


def get(url, params=None):
    http = httplib2.Http()
    if params is not None:
        param = parse.urlencode(params)
        url += '?' + param
    resp, content = http.request(url, 'GET')
    status = resp.get('status')
    if status != '200':
        raise Exception('The server responses {}'.format(status))
    return json.loads(content.decode('utf-8'))
