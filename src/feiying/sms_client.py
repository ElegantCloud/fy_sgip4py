#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
SMS Client
"""
import urllib
import logging
import logging.handlers

# config logger
log_name = 'sms_client'
logger = logging.getLogger(log_name)
logger.setLevel(logging.DEBUG)
lh = logging.handlers.TimedRotatingFileHandler('/tmp/'+ log_name + '.log', when = 'midnight')
lh.setLevel(logging.INFO)
lf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
lh.setFormatter(lf)
logger.addHandler(lh)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)


class SMSClient(object):
    instance = None
    
    def __init__(self):
        self._url = "http://221.179.180.158:9000/QxtSms/QxtFirewall"
        self._username = "njftwl"
        self._pwd = "ft123456"

    def send_sms(self, phone_number, message):
        message = message.decode('utf-8').encode('gbk')
        param = urllib.urlencode({'OperID': self._username, 'OperPass': self._pwd, 'DesMobile': phone_number, 'Content': message, 'ContentType': 15})
        #param = 'OperID=' + self._username + '&OperPass=' + self._pwd + '&DesMobile=' + phone_number + '&Content=' + message + '&ContentType=15'
        f = urllib.urlopen(self._url + "?%s" % param)
        return f.readline()

    @classmethod
    def get_instance(cls):
        if cls.instance == None:
            cls.instance = SMSClient()
        return cls.instance

def send_sms(phone_number, message):
    sc = SMSClient.get_instance()
    ret = sc.send_sms(phone_number, message)
    logger.info('send sms return: %s', ret)
    return ret

# test
if __name__ == "__main__":
    msg = '你好China'
    ret = send_sms('13813005146', msg)


