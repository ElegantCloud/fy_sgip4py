#! /usr/bin/env python

"""
 SGIP server for receiving SGIP message from SMG
"""
from optparse import OptionParser
import eventlet
from sgip import *
import oursql

db_host = 'fy1.richitec.com'
db_user = 'feiying'
db_pwd = 'feiying123'
db_name = 'feiying'

# SGIP Message Processor
class SGIPProcessor(object):
    def __init__(self, ssd):
        self.ssock = ssd
      
    # receive data by specified size
    def __recv(self, size):
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
        raw_data = self.__recv(SGIPHeader.size())
        header = SGIPHeader()
        header.unpack(raw_data)
        return header
    
    # process SGIP message
    def process(self):
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
        if sgip_msg == None or header == None:
            return
        seq_num = header.SequenceNumber[:]
        msgHeader = SGIPHeader(SGIPHeader.size() + sgip_msg.size(), sgip_msg.ID, seq_num)
        sgip_msg.header = msgHeader
        raw_data = sgip_msg.pack()
        self.__send(raw_data)

    def __send_sgip_unbind_resp(self, header):
        unbindRespMsg = SGIPUnbindResp()
        self.__send_sgip_msg(unbindRespMsg, header)

    def __handle_bind_msg(self, header):
        # continue to receive bind msg body
        raw_data = self.__recv(SGIPBind.size())
        bindMsg = SGIPBind()
        bindMsg.unpackBody(raw_data)
        # skip authentication for SMG
        # send Bind Resp
        bindRespMsg = SGIPBindResp()
        self.__send_sgip_msg(bindRespMsg, header)

    def __handle_deliver_msg(self, header):
        # continue to receive deliver msg body
        raw_data = self.__recv(SGIPDeliver.size())
        deliverMsg = SGIPDeliver()
        deliverMsg.unpackBody(raw_data)
        # send Deliver Resp
        deliverRespMsg = SGIPDeliverResp()
        self.__send_sgip_msg(deliverRespMsg, header)
        # process Deliver Msg content
        self.__process_deliver_content(deliverMsg) 

    # do actual work according to the content of deliver message
    def __process_deliver_content(self, deliverMsg):
        userNumber = deliverMsg.UserNumber
        msg_content = deliverMsg.MessageContent
        status = ''
        if 'DZFY' in msg_content:
            # update the business status as opened
            status = 'opened'
        elif 'TDFY' in msg_content:
            # update the business status as unopened
            status = 'unopened'

        # update database
        dbconn = oursql.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name)
        with dbconn.cursor(oursql.DictCursor) as cursor:
            print 'updating business status in database'
            sql = "UPDATE fy_user SET userkey = 'asdf' AND business_status = '%s' WHERE username = '%s'" % (status, userNumber)
            cursor.execute(sql, plain_query = True)
        dbconn.close()


    





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
            pool.spawn_n(handleMsg, new_sock)
        except (SystemExit, KeyboardInterrupt):
            print 'server caught exception'
            break;

    return


if __name__ == "__main__":
    main()





