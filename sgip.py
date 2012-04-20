#! /usr/bin/env python

"""
SGIP message defininitions and operations
"""

from struct import *

# Ancestor of all Messages
class BaseMSG(object):
    fmt = ''  # struct format
    struct_tool = None
    def __init__(self):
        self.struct_tool = Struct(self.fmt)

    # unpack message from raw data
    def unpack(self, raw_msg):
        pass

    # get message size
    @classmethod
    def size(cls):
        return calcsize(cls.fmt)

    
# define SGIP Header
class SGIPHeader(BaseMSG):
    fmt = '!II3I' # struct format

    def __init__(self, msg_len = 20, command_id = 0, seq_num = [0, 0, 0]):
        super(SGIPHeader, self).__init__()
        self.MessageLength = msg_len
        self.CommandID = command_id
        self.SequenceNumber = seq_num

    # unpack the message header from raw message data 
    def unpack(self, raw_msg):
        header_tuple = self.struct_tool.unpack(raw_msg)
        self.MessageLength = header_tuple[0]
        self.CommandID = header_tuple[1]
        self.SequenceNumber = list(header_tuple[2:])


# define SGIP base message
class BaseSGIPMSG(BaseMSG):
    
    def __init__(self):
        super(BaseSGIPMSG, self).__init__()
        self._header = SGIPHeader()
    
    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, sgip_header):
        self._header = sgip_header
    
    # pack the header and body into raw message data
    def pack(self):
        pass

    # unpack the message body from raw message data
    def unpackBody(self, raw_msg):
        pass


# SGIP Bind Message
class SGIPBind(BaseSGIPMSG):
    fmt = '!B16s16s8s'

    def __init__(self, login_type = 1, login_name = '', login_pwd = '', reserve = ''):
        super(SGIPBind, self).__init__()
        self.LoginType = login_type
        self.LoginName = login_name
        self.LoginPassword = login_pwd
        self.Reserve = reserve

    def unpackBody(self, raw_msg):
        body_tuple = self.struct_tool.unpack(raw_msg)
        self.LoginType = body_tuple[0]
        self.LoginName = body_tuple[1]
        self.LoginPassword = body_tuple[2]
        self.Reserve = body_tuple[3]

    def pack(self):
        self_fmt = self.fmt[1:]
        msg_fmt = self.header.fmt + self_fmt
        print 'bind format: ', msg_fmt
        raw_msg = pack(msg_fmt, self.header.MessageLength, self.header.CommandID, self.header.SequenceNumber[0], self.header.SequenceNumber[1], self.header.SequenceNumber[2], self.LoginType, self.LoginName, self.LoginPassword, self.Reserve) 
        return raw_msg


## for test
if __name__ == "__main__":
    header = SGIPHeader()
    raw_msg = pack('!II3I', 30, 1, 2, 1, 2)
    header.unpack(raw_msg)

    print 'Header: ', header.MessageLength, ' ', header.CommandID, ' ', header.SequenceNumber
    print 'Header size: ', SGIPHeader.size()
    print 'Base Msg size: ', BaseMSG.size()

    bind = SGIPBind()
    bind.header = header
    print 'BIND Msg size: ', SGIPBind.size()
    raw_msg = bind.pack()
    print 'Bind Raw Msg: ', raw_msg
   
    raw_msg = pack('!B16s16s8s', 2, 'starkingwx', 'abc', 'blank')
    bind.unpackBody(raw_msg)
    print "Bind body: ", bind.LoginType, ' ', bind.LoginName, ' ', bind.LoginPassword, ' ', bind.Reserve

