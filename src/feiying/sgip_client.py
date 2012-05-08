#! /usr/bin/env python
# coding: gbk

"""
SGIP Message Send
"""

from datetime import datetime
import eventlet
from eventlet.green import socket
from sgip import *
from binascii import *
import logging
import logging.handlers

# config logger
log_name = 'sgip_client'
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

    def __init__(self, host, port, corp_id, username, pwd, sp_number):
        self._host = host
        self._port = port
        self._corp_id = corp_id
        self._username = username
        self._pwd = pwd
        self._seq_id = 0
        self._sp_number = sp_number 

    def _init_sgip_connection(self):
        self.__csock = socket.socket()
        ip = socket.gethostbyname(self._host)
        self.__csock.connect((ip, self._port))
        logger.info('%s connected' % self._host)

    def _close_sgip_connection(self):
        if self.__csock != None:
            self.__csock.close()
        logger.info('connection to %s closed' % self._host)

    def gen_seq_number(self):
    	seq_num1 = 3055122870
        today = datetime.today()
        seq_num2 = (((today.month * 100 + today.day) * 100 + today.hour) * 100 + today.minute) * 100 + today.second
        seq_num3 = self._seq_id
        self._seq_id += 1
        return [seq_num1, seq_num2, seq_num3]

    def send_data(self, data):
        logger.info('send data: %s', hexlify(data))
        fd = self.__csock.makefile('w')
        fd.write(data)
        fd.flush()
        fd.close()

    def recv_data(self, size):
        fd = self.__csock.makefile('r')
        data = fd.read(size)
        logger.info('recv raw data: %s', hexlify(data))
        i = 0 
        while len(data) < size:
            nleft = size - len(data)
            t_data = fd.read(nleft)
            #logger.info('i: ' + i + ' data: ' + hexlify(t_data) )
            i += 1
	    data = data + t_data
        fd.close()
        return data

    def _bind(self):
        logger.info('do bind')
        # send bind msg
        bindMsg = SGIPBind(1, self._username, self._pwd)
        header = SGIPHeader(SGIPHeader.size() + bindMsg.size(), SGIPBind.ID, self.gen_seq_number())
        bindMsg.header = header
        raw_data = bindMsg.pack()
        self.send_data(raw_data)
        # recv bind resp msg
        resp_header_data = self.recv_data(SGIPHeader.size())
        logger.info('header raw data: %s', hexlify(resp_header_data) )
        
        respHeader = SGIPHeader()
        respHeader.unpack(resp_header_data)
        logger.info('resp command id: {0}'.format(respHeader.CommandID))
        resp_body_data = self.recv_data(SGIPBindResp.size())
        bindRespMsg = SGIPBindResp()
        bindRespMsg.unpackBody(resp_body_data)
        if respHeader.CommandID == SGIPBindResp.ID and bindRespMsg.Result == 0:
            return True
        else:
            return False
    
    def _unbind(self):
        logger.info('do unbind')
        unbindMsg = SGIPUnbind()
        header = SGIPHeader(SGIPHeader.size() + unbindMsg.size(), SGIPUnbind.ID)
        unbindMsg.header = header
        raw_data = unbindMsg.pack()
        self.send_data(raw_data)

    def _submit(self, userNumber, message):
        logger.info('do submit')
        # send submit msg
        submitMsg = SGIPSubmit(sp_number = self._sp_number, user_number = userNumber, corp_id = self._corp_id, msg_len = len(message), msg_content = message)
        header = SGIPHeader(SGIPHeader.size() + submitMsg.mySize(), SGIPSubmit.ID)
        submitMsg.header = header
        raw_data = submitMsg.pack()
        self.send_data(raw_data)
        # recv submit msg
        resp_header_data = self.recv_data(SGIPHeader.size())
        resp_body_data = self.recv_data(SGIPSubmitResp.size())
        submitRespMsg = SGIPSubmitResp()
        submitRespMsg.unpackBody(resp_body_data)
        respheader = SGIPHeader()
        respheader.unpack(resp_header_data)
        if respheader.CommandID == SGIPSubmitResp.ID and submitRespMsg.Result == 0:
            logger.info('sms submitted ok')

    def send_sms(self, user_number, message):
        try:
            self._init_sgip_connection()
            bindRet = self._bind() 
            if bindRet:
                # submit msg
                self._submit(user_number, message)
            else:
                logger.info('bind failed')
            self._unbind()
        except socket.error as (errno, strerror):
            logger.info("socket error({0}): {1}".format(errno, strerror))
        finally:
            self._close_sgip_connection()
   

## for test
if __name__ == "__main__":
    client = SMSClient(host = '220.195.192.85', port = 8801, corp_id = '22870', username = 'fy', pwd = 'f75y', sp_number = '1065583398')
    client.send_sms('18655165434', '你好China')

