# -*- coding:utf-8 -*-
import os
import datetime
import logging

filename = 'checker_' + str(os.getpid()) + '.log'
logging.basicConfig(filename=filename)
logger = logging.getLogger(__name__).setLevel(logging.DEBUG)

class Checker(object):
    def __init__(self, name, mtype=None, max_len=None):
        self.name = name
        self.type = mtype
        self.max_len = max_len
        self.value = None
    def check(self, value):
        if value is None:
            self.value = None
            return True
        if value == '':
            self.value == ''
            return True

        if self.type == 'text':
            if isinstance(value, int):
                self.value = str(value)
            elif isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, str):
                self.value = value
            else:
                logger.debug(" [inserter] ({}-{})Type(text) error!".format(self.name, value))
                return False

        elif self.type == 'string':
            if isinstance(value, int):
                self.value = str(value)
            elif isinstance(value, str):
                if len(value) > self.max_len:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                self.value = value
            elif isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                logger.debug(" [inserter] ({}-{})Type(string) error!".format(self.name, value))
                return False

        elif self.type == 'integer':
            if isinstance(value, int):
                self.value = value
            elif isinstance(value, str):
                if len(value) > self.max_len:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                if not value.isdigit():
                    logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                    return False
                self.value = int(value)
            else:
                logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                return False

        elif self.type == 'datetime':
            if isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, str):
                # len('2015-04-19 12:20:00') = 20
                if len(value) > 20:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                self.value = value
                # self.value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                return False
            return True
        else:
            logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
            return False
        return True

