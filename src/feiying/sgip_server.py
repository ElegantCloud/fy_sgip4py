#! /usr/bin/env python

"""
 SGIP server for receiving SGIP message from SMG
"""
from optparse import OptionParser
import eventlet

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





