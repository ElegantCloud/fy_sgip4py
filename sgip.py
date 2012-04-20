#! /usr/bin/env python

"""
SGIP message defininitions and operations
"""

from struct import *

class BaseMSG(object):
    fmt = ''  # struct format
    struct_tool = None
    def __init__(self):
        print 'init struct tool'
        self.struct_tool = Struct(self.fmt)

    def unpack(self, raw_msg):
        pass

    # message size
    @classmethod
    def size(cls):
        return calcsize(cls.fmt)

    
# define Message Header
class MSGHeader(BaseMSG):
    fmt = '!II3I' # struct format
    #__struct_tool = Struct(fmt)

    #size = calcsize(fmt) # size of message header

    def __init__(self, msg_len = 20, command_id = 0, seq_num = [0, 0, 0]):
        super(MSGHeader, self).__init__()
        self.MessageLength = msg_len
        self.CommandID = command_id
        self.SequenceNumber = seq_num

    def unpack(self, raw_msg):
        header_tuple = self.struct_tool.unpack(raw_msg)
        self.MessageLength = header_tuple[0]
        self.CommandID = header_tuple[1]
        self.SequenceNumber = list(header_tuple[2:])



## for test
if __name__ == "__main__":
    header = MSGHeader()
    raw_msg = pack('!II3I', 30, 1, 2, 1, 2)
    header.unpack(raw_msg)

    print header.MessageLength, ' ', header.CommandID, ' ', header.SequenceNumber
    print 'Header size: ', MSGHeader.size()
    print 'Base Msg size: ', BaseMSG.size()
