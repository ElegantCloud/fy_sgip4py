#! /usr/bin/env python

"""
 SGIP server for receiving SGIP message from SMG
"""
from optparse import OptionParser
import eventlet
from sgip import *


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
                pass
            elif header.CommandID == SGIPDeliver.ID:
                pass
            elif header.CommandID == SGIPUnbind.ID:
                break

        self.ssock.close() 


    def __send_sgip_unbind_resp(self, header):
        pass




def handleMsg(ssd):
    fd = ssd.makefile('rw')
    print 'client connected'
    message = ''
    while True:
        x = fd.readline()
        print 'receive: ', x, ' len: ', len(x)
        if x == "\r\n": break
        message += x
    fd.write(message)
    fd.flush()
    fd.close()
    ssd.close()
    print "echoed", message
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





