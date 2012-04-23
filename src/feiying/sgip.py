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
        self_fmt = self.fmt[1:]
        msg_fmt = self.header.fmt + self_fmt
        print 'SGIP MSG format: ', msg_fmt
        raw_msg = self._pack(msg_fmt)
        return raw_msg

    # pack the message into raw data, this method should be implemented by subclasses
    def _pack(self, msg_fmt):
        return ''

    # unpack the message body from raw message data
    def unpackBody(self, raw_msg):
        pass

# define Base SGIP Resp Message
class BaseSGIPResp(BaseSGIPMSG):
    fmt = '!B8s'

    def __init__(self, result = 0, reserve = ''):
        super(BaseSGIPResp, self).__init__()
        self.Result = result
        self.Reserve = reserve

    def unpackBody(self, raw_msg):
        body_tuple = self.struct_tool.unpack(raw_msg)
        self.Result = body_tuple[0]
        self.Reserve = body_tuple[1]

    def _pack(self, msg_fmt):
        raw_msg = pack(msg_fmt, self.header.MessageLength, self.header.CommandID, self.header.SequenceNumber[0], self.header.SequenceNumber[1], self.header.SequenceNumber[2], self.Result, self.Reserve)
        return raw_msg


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

    def _pack(self, msg_fmt):
        raw_msg = pack(msg_fmt, self.header.MessageLength, self.header.CommandID, self.header.SequenceNumber[0], self.header.SequenceNumber[1], self.header.SequenceNumber[2], self.LoginType, self.LoginName, self.LoginPassword, self.Reserve) 
        return raw_msg

# SGIP Bind Resp Message
class SGIPBindResp(BaseSGIPResp):
    def __init__(self, result = 0, reserve = ''):
        super(SGIPBindResp, self).__init__(result, reserve)


# SGIP Deliver Message
class SGIPDeliver(BaseSGIPMSG):
    fmt = '!21s21s3BI140s8s'

    def __init__(self, user_number = '', sp_number = '', tp_pid = 0, tp_udhi = 0, msg_code = 0, msg_len = 0, msg_content = '', reserve = ''):
        super(SGIPDeliver, self).__init__()
        self.UserNumber = user_number
        self.SPNumber = sp_number
        self.TP_pid = tp_pid
        self.TP_udhi = tp_udhi
        self.MessageCoding = msg_code
        self.MessageLength = msg_len
        self.MessageContent = msg_content
        self.Reserve = reserve

    def unpackBody(self, raw_msg):
        body_tuple = self.struct_tool.unpack(raw_msg)
        self.UserNumber = body_tuple[0]
        self.SPNumber = body_tuple[1]
        self.TP_pid = body_tuple[2]
        self.TP_udhi = body_tuple[3]
        self.MessageCoding = body_tuple[4]
        self.MessageLength = body_tuple[5]
        self.MessageContent = body_tuple[6]
        self.Reserve = body_tuple[7]

    def _pack(self, msg_fmt):
        raw_msg = pack(msg_fmt, self.header.MessageLength, self.header.CommandID, self.header.SequenceNumber[0], self.header.SequenceNumber[1], self.header.SequenceNumber[2], self.UserNumber, self.SPNumber, self.TP_pid, self.TP_udhi, self.MessageCoding, self.MessageLength, self.MessageContent, self.Reserve)
        return raw_msg


# SGIP Deliver Resp Message
class SGIPDeliverResp(BaseSGIPResp):
    def __init__(self, result = 0, reserve = ''):
        super(SGIPDeliverResp, self).__init__(result, reserve)


# SGIP Report Message
class SGIPReport(BaseSGIPMSG):
    fmt = '!3IB21s2B8s'

    def __init__(self, submit_seq_num = [0, 0, 0], report_type = 1, user_number = '', state = 0, error_code = 0, reserve = ''):
        super(SGIPReport, self).__init__()
        self.SubmitSequenceNumber = submit_seq_num
        self.ReportType = report_type
        self.UserNumber = user_number
        self.State = state
        self.ErrorCode = error_code
        self.Reserve = reserve

    def unpackBody(self, raw_msg):
        body_tuple = self.struct_tool.unpack(raw_msg)
        self.SubmitSequenceNumber = list(body_tuple[0:3])
        self.ReportType = body_tuple[3]
        self.UserNumber = body_tuple[4]
        self.State = body_tuple[5]
        self.ErrorCode = body_tuple[6]
        self.Reserve = body_tuple[7]
    
    def _pack(self, msg_fmt):
        raw_msg = pack(msg_fmt, self.header.MessageLength, self.header.CommandID, self.header.SequenceNumber[0], self.header.SequenceNumber[1], self.header.SequenceNumber[2], self.SubmitSequenceNumber[0], self.SubmitSequenceNumber[1], self.SubmitSequenceNumber[2], self.ReportType, self.UserNumber, self.State, self.ErrorCode, self.Reserve)
        return raw_msg

# SGIP Report Resp Message
class SGIPReportResp(BaseSGIPResp):
    def __init__(self, result = 0, reserve = ''):
        super(SGIPReportResp, self).__init__(result, reserve)


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

