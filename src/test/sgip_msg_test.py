from feiying import sgip
import unittest
from struct import *

class TestSGIPBindResp(unittest.TestCase):
    def setUp(self):
        self.sgip_bind_resp = sgip.SGIPBindResp(2, 'hello')
        self.raw_data = pack('!B8s', 1, 'good') 

    def test_unpack(self):
        self.sgip_bind_resp.unpackBody(self.raw_data)
        self.assertEqual(self.sgip_bind_resp.Result, 1)
        self.assertTrue('good' in self.sgip_bind_resp.Reserve)

class TestSGIPDeliver(unittest.TestCase):
    def setUp(self):
        self.sgip_deliver = sgip.SGIPDeliver()
<<<<<<< HEAD
        self.raw_data = pack('!21s21s3BI197s8s', '13813005146', '10010', 1, 2, 3, 140, 'nice day', 'temp')
=======
        self.raw_data = pack('!21s21s3BI8s8s', '13813005146', '10010', 1, 2, 3, 8, 'nice day', 'temp')
        self.sgip_deliver.contentLength = 8
>>>>>>> ed0ebf3335a71ae89eee22fd42a2d881c78796fe

    def test_unpack(self):
        self.sgip_deliver.unpackBody(self.raw_data)
        self.assertTrue('13813005146' in self.sgip_deliver.UserNumber)
        self.assertTrue('10010' in self.sgip_deliver.SPNumber)
        self.assertEqual(self.sgip_deliver.TP_pid, 1)
        self.assertEqual(self.sgip_deliver.TP_udhi, 2)
        self.assertEqual(self.sgip_deliver.MessageCoding, 3)
        self.assertEqual(self.sgip_deliver.MessageLength, 8)
        self.assertTrue('nice day' in self.sgip_deliver.MessageContent)
        self.assertTrue('temp' in self.sgip_deliver.Reserve)

class TestSGIPDeliverResp(unittest.TestCase):
    def setUp(self):
        self.sgip_deliver_resp = sgip.SGIPDeliverResp()
        self.raw_data = pack('!B8s', 1, 'nice')

    def test_unpack(self):
        self.sgip_deliver_resp.unpackBody(self.raw_data)
        self.assertEqual(self.sgip_deliver_resp.Result, 1)
        self.assertTrue('nice' in self.sgip_deliver_resp.Reserve)

class TestSGIPReport(unittest.TestCase):
    def setUp(self):
        self.sgip_report = sgip.SGIPReport()
        self.raw_data = pack('!3IB21s2B8s', 1, 2, 3, 4, '13813005146', 1, 2, 'temp')

    def test_unpack(self):
        self.sgip_report.unpackBody(self.raw_data)
        self.assertEqual(self.sgip_report.SubmitSequenceNumber, [1, 2, 3])
        self.assertEqual(self.sgip_report.ReportType, 4)
        self.assertTrue('13813005146' in self.sgip_report.UserNumber)
        self.assertEqual(self.sgip_report.State, 1)
        self.assertEqual(self.sgip_report.ErrorCode, 2)
        self.assertTrue('temp' in self.sgip_report.Reserve)

class TestSGIPReportResp(unittest.TestCase):
    def setUp(self):
        self.sgip_report_resp = sgip.SGIPReportResp()
        self.raw_data = pack('!B8s', 1, 'temp')

    def test_unpack(self):
        self.sgip_report_resp.unpackBody(self.raw_data)
        self.assertEqual(self.sgip_report_resp.Result, 1)
        self.assertTrue('temp' in self.sgip_report_resp.Reserve)

class TestSGIPSubmit(unittest.TestCase):
    def setUp(self):
        self.sp_number = '1065583398'
        self.charge_number = '000000000000000000000'
        self.user_count = 1
        self.user_number = '13813005146'
        self.corp_id = '22870'
        self.service_type = 'test'
        self.fee_type = 0
        self.fee_value = '0'
        self.given_value = '0'
        self.agent_flag = 0
        self.morelateto_mt_flag = 1
        self.priority = 0
        self.expire_time = ''
        self.schedule_time = ''
        self.report_flag = 1
        self.tp_pid = 0
        self.tp_udhi = 0
        self.msg_coding = 15
        self.msg_type = 0
        self.msg_content = "中国人民"
        self.msg_len = len(self.msg_content)
        print 'msg len: ', self.msg_len
        self.reserve = ''

        self.sgip_submit = sgip.SGIPSubmit(self.sp_number, self.charge_number, self.user_count, self.user_number, self.corp_id, self.service_type, self.fee_type, self.fee_value, self.given_value, self.agent_flag, self.morelateto_mt_flag, self.priority, self.expire_time, self.schedule_time, self.report_flag, self.tp_pid, self.tp_udhi, self.msg_coding, self.msg_type, self.msg_len, self.msg_content, self.reserve)
        self.raw_data = pack(self.sgip_submit.myFmt,self.sp_number, self.charge_number, self.user_count, self.user_number, self.corp_id, self.service_type, self.fee_type, self.fee_value, self.given_value, self.agent_flag, self.morelateto_mt_flag, self.priority, self.expire_time, self.schedule_time, self.report_flag, self.tp_pid, self.tp_udhi, self.msg_coding, self.msg_type, self.msg_len, self.msg_content, self.reserve) 

    def test_unpack(self):
        self.sgip_submit.unpackBody(self.raw_data)
        self.assertTrue(self.sp_number in self.sgip_submit.SPNumber)
        self.assertEqual(self.sgip_submit.ChargeNumber, self.charge_number)
        self.assertEqual(self.sgip_submit.UserCount, self.user_count)
        self.assertTrue(self.user_number, self.sgip_submit.UserNumber)
        self.assertEqual(self.sgip_submit.CorpId, self.corp_id)
        self.assertTrue(self.service_type, self.sgip_submit.ServiceType)
        self.assertEqual(self.fee_type, self.sgip_submit.FeeType)
        self.assertTrue(self.fee_value, self.sgip_submit.FeeValue)
        self.assertTrue(self.given_value in self.sgip_submit.GivenValue)
        self.assertEqual(self.sgip_submit.AgentFlag, self.agent_flag)
        self.assertEqual(self.sgip_submit.MorelatetoMTFlag, self.morelateto_mt_flag)
        self.assertEqual(self.sgip_submit.Priority, self.priority)
        self.assertTrue(self.expire_time in self.sgip_submit.ExpireTime)
        self.assertTrue(self.schedule_time in self.sgip_submit.ScheduleTime)
        self.assertEqual(self.sgip_submit.ReportFlag, self.report_flag)
        self.assertEqual(self.sgip_submit.TP_pid, self.tp_pid)
        self.assertEqual(self.sgip_submit.TP_udhi, self.tp_udhi)
        self.assertEqual(self.sgip_submit.MessageCoding, self.msg_coding)
        self.assertEqual(self.sgip_submit.MessageType, self.msg_type)
        self.assertEqual(self.sgip_submit.MessageLength, self.msg_len)
        self.assertEqual(self.sgip_submit.MessageContent, self.msg_content)
        self.assertTrue(self.reserve in self.sgip_submit.Reserve)

if __name__ == '__main__':
    unittest.main()




