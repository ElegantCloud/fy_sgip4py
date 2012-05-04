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
        self.raw_data = pack('!21s21s3BI197s8s', '13813005146', '10010', 1, 2, 3, 140, 'nice day', 'temp')

    def test_unpack(self):
        self.sgip_deliver.unpackBody(self.raw_data)
        self.assertTrue('13813005146' in self.sgip_deliver.UserNumber)
        self.assertTrue('10010' in self.sgip_deliver.SPNumber)
        self.assertEqual(self.sgip_deliver.TP_pid, 1)
        self.assertEqual(self.sgip_deliver.TP_udhi, 2)
        self.assertEqual(self.sgip_deliver.MessageCoding, 3)
        self.assertEqual(self.sgip_deliver.MessageLength, 140)
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



if __name__ == '__main__':
    unittest.main()




