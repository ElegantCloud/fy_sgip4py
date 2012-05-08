#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
 SGIP server for receiving SGIP message from SMG
"""
from optparse import OptionParser
import eventlet
from sgip import *
import oursql
from binascii import *
from sms_client import *


# database config
db_host = 'fy1.richitec.com'
db_user = 'feiying'
db_pwd = 'feiying123'
db_name = 'feiying'

# allowed SMG addresses
SMG_ADDRS = ('220.195.192.85', '127.0.0.1')

# respone messages
DZFY_OK = '尊敬的客户：您已成功订购飞影业务，请进入http://fy1.richitec.com/feiying/mobile下载客户端'
TDFY_OK = '尊敬的客户：您已成功退订飞影业务，感谢您的使用。'
DZFY_FAIL = '尊敬的客户：您已订购过飞影业务，请勿重复订购。'
TDFY_FAIL = '尊敬的客户：您尚未开通飞影业务，无法执行退订操作。'

# SGIP Message Processor
class SGIPProcessor(object):
    def __init__(self, ssd):
        self.ssock = ssd
      
    # receive data by specified size
    def __recv(self, size):
        print '...receiving raw data...'
        fd = self.ssock.makefile('r')
        data = fd.read(size)
        while len(data) < size:
            nleft = size - len(data) 
            t_data = fd.read(nleft)
            data = data + t_data
        fd.close()
        return data

    # send data
    def __send(self, data):
        fd = self.ssock.makefile('w')
        fd.write(data)
        fd.flush()
        fd.close()

    # read SGIP message header
    def __read_msg_header(self):
        print 'read msg header'
        raw_data = self.__recv(SGIPHeader.size())
        print '# header raw data: ', hexlify(raw_data)
        header = SGIPHeader()
        header.unpack(raw_data)
    	print '# msg len: ', header.MessageLength
	print '# command id: ', header.CommandID
	print '# sequence number: {0} {1} {2}'.format(header.SequenceNumber[0], header.SequenceNumber[1], header.SequenceNumber[2])
        return header
    
    # process SGIP message
    def process(self):
        print 'process SGIP message'
        while True:
            # read message header
            header = self.__read_msg_header()
            if header.CommandID == SGIPBind.ID:
                self.__handle_bind_msg(header) 
            elif header.CommandID == SGIPDeliver.ID:
                self.__handle_deliver_msg(header) 
            elif header.CommandID == SGIPUnbind.ID:
                self.__send_sgip_unbind_resp(header)
                break

        self.ssock.close() 
   
    # send SGIP message
    def __send_sgip_msg(self, sgip_msg, header):
        print 'send sgip msg'
        if sgip_msg == None or header == None:
            return
        seq_num = header.SequenceNumber[:]
        msgHeader = SGIPHeader(SGIPHeader.size() + sgip_msg.size(), sgip_msg.ID, seq_num)
        sgip_msg.header = msgHeader
        raw_data = sgip_msg.pack()
        print '# send raw data: ', hexlify(raw_data)
        self.__send(raw_data)

    def __send_sgip_unbind_resp(self, header):
        print 'send unbind resp'
        unbindRespMsg = SGIPUnbindResp()
        self.__send_sgip_msg(unbindRespMsg, header)

    def __handle_bind_msg(self, header):
        print 'handle bind msg'
        # continue to receive bind msg body
        raw_data = self.__recv(SGIPBind.size())
        print '# bind raw data: ', hexlify(raw_data)
        bindMsg = SGIPBind()
        bindMsg.unpackBody(raw_data)
        # skip authentication for SMG
       	#print 'login type: ', bindMsg.LoginType
        #print 'login name: ', bindMsg.LoginName
        #print 'login pwd: ', bindMsg.LoginPassword 

	# send Bind Resp
        print 'send bind resp'
        bindRespMsg = SGIPBindResp()
        self.__send_sgip_msg(bindRespMsg, header)

    def __handle_deliver_msg(self, header):
        print 'handle deliver msg'
        # continue to receive deliver msg body
        deliver_msg_len = header.MessageLength - header.size()
        print ' deliver msg len: %d' % deliver_msg_len
        raw_data = self.__recv(deliver_msg_len)
        print '# deliver raw data: ', hexlify(raw_data)
        deliverMsg = SGIPDeliver()
        deliverMsg.contentLength = deliver_msg_len - SGIPDeliver.size()
        print 'msg content len: %d - SGIPDeliver origin size: %d' % (deliverMsg.contentLength, SGIPDeliver.size())
        deliverMsg.unpackBody(raw_data)
        # send Deliver Resp
        print 'send deliver resp'
        deliverRespMsg = SGIPDeliverResp()
        self.__send_sgip_msg(deliverRespMsg, header)
        # process Deliver Msg content
        self._process_deliver_content(deliverMsg) 

    # do actual work according to the content of deliver message
    def _process_deliver_content(self, deliverMsg):
        print 'process deliver content'
        if deliverMsg.UserNumber.find('86') == 0:
            userNumber = deliverMsg.UserNumber[2:]
        else:
            userNumber = deliverMsg.UserNumber
        msg_content = deliverMsg.MessageContent
        print 'msg content: %s' % msg_content
        status = ''
        if 'DZFY' == msg_content:
            # update the business status as opened
            status = 'opened'
        elif 'TDFY' == msg_content:
            # update the business status as unopened
            status = 'unopened'

        if status != '':
            dbconn = oursql.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name)

            with dbconn.cursor(oursql.DictCursor) as cursor:
                # check user status
                print 'check user status'
                sql = "SELECT business_status FROM fy_user WHERE username = ?"
                cursor.execute(sql, (userNumber,))
                result = cursor.fetchone()
                if result != None:
                    exist_status = result['business_status']
                    if msg_content == 'DZFY':
                        if 'opened' == exist_status:
                            # notice user that he has subscribed 
                            print 'DZFY fail'
                            send_sms(userNumber, DZFY_FAIL) 
                        else:
                            # update user business status as opened for user is subscribing 
                            self._update_status(cursor, userNumber, status)
                            send_sms(userNumber, DZFY_OK)
                    elif msg_content == 'TDFY':
                        if 'unopened' == exist_status:
                            # notice user that he hasn't subscribed, no need to unsubscribe 
                            print 'TDFY fail'
                            send_sms(userNumber, TDFY_FAIL)
                        else:
                            # update user business_status as unopened for user is unsubscribing
                            self._update_status(cursor, userNumber, status)
                            send_sms(userNumber, TDFY_OK)
                else:
                    # no user found
                    if msg_content == 'DZFY':
                        # insert new user and set business_status as opened
                        print "user doesn't exist, insert it as opened"
                        sql = "INSERT INTO fy_user(username, userkey, business_status) VALUES(?, 'asdf', ?)"
                        try:
                            cursor.execute(sql, (userNumber, status))
                        except:
                            pass
                        send_sms(userNumber, DZFY_OK)

                    elif msg_content == 'TDFY':
                        # notice user that he hasn't subscribed, no need to unsubscribe
                        print "user doesn't exist, TDFY fail"
                        send_sms(userNumber, TDFY_FAIL)

            dbconn.close()

    # update business status in database
    def _update_status(self, cursor, userNumber, status):
        # update database
        print 'updating business status in database - status: %s userNumber: %s' % (status, userNumber)
        sql = "UPDATE `fy_user` SET `userkey` = 'asdf', `business_status` = ? WHERE `username` = ? " 
        cursor.execute(sql, (status, userNumber))
    
def handleMsg(ssd):
    print 'client connected'
    processor = SGIPProcessor(ssd)
    processor.process()
    print "close connection"

def main():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest = "port", help = "input port to listen", default = 8801)
    (options, args) = parser.parse_args()

    print "server is listening on port %d" % options.port
    server = eventlet.listen(('0.0.0.0', options.port))
    pool = eventlet.GreenPool(100000)
    while True:
        try:
            new_sock, address = server.accept()
            print "accepted ", address
            if address[0] in SMG_ADDRS:
                pool.spawn_n(handleMsg, new_sock)
            else:
                print 'illegal SMG addr: %s - close' % address[0]
                new_sock.close()
        except (SystemExit, KeyboardInterrupt):
            print 'server caught exception'
            break;

    return


if __name__ == "__main__":
    main()
