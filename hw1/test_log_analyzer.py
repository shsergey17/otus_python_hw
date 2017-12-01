#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import log_analyzer

#nginx-access[^\d]*(\d{8})[\.gz]*

class TestMethods(unittest.TestCase):

    def test_get_last_logfile(self):
        filename = os.path.join("./", "test-20170601")
        with open(filename, "w", buffering=-1) as file:
            file.write("test")

        log_analyzer.config["LOG_TEMPLATE"] = "test-(\d{8})[\.gz]*"
        self.assertEqual(log_analyzer.get_last_logfile("./"), {"maxdate":'2017-06-01', "logfile":'./test-20170601'})
        os.remove(filename)


    def test_get_stat(self):
        lines = [['test', 1]]
        ok = [{'count': 1, 'time_avg': 1.0, 'time_max': 1.0, 'time_sum': 1.0, 'url': 'test', 'time_med': 1.0,
        'time_perc': 100.0, 'percent': 100.0}]
        self.assertEqual(log_analyzer.get_stat(lines), ok)


    def test_median(self):
        self.assertEqual(log_analyzer.median([1,2,3,4,5,6]), 3.5)


    def test_process_line(self):
        text = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25047606 HTTP/1.1" 200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""
        self.assertEqual(log_analyzer.process_line(text), ['/api/v2/banner/25047606', '2.490'])


    def test_xreadlines(self):
        filename = os.path.join("./", "test-20170601")
        text = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25047606 HTTP/1.1" 200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""
        with open(filename, "w", buffering=-1) as file:
            file.write(text)

        for a in log_analyzer.xreadlines(filename):
            res = a
        self.assertEqual(res, ['/api/v2/banner/25047606', '2.490'])
        os.remove(filename)


    def test_create_ts(self):
        filename = "./test.ts"
        log_analyzer.create_ts("./test.ts")
        with open(filename, "r") as file:
            ts = file.read()

        self.assertEqual(len(ts), 10)
        os.remove(filename)


    def test_bad_gz(self):
        filename = "./test/nginx-access-ui-bad.log-20170731.gz"

        with self.assertRaises(Exception):
            res = log_analyzer.xreadlines(filename)
            res.next()


    def test_log_file_not_found(self):
        with self.assertRaises(Exception):
            log_analyzer.get_last_logfile("./folder_not_exists")


    def test_bad_line(self):
        text_1 = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25047606 HTTP/1.1" 200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""
        text_2 = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300]  200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""

        self.assertEqual(log_analyzer.process_line(text_1), ['/api/v2/banner/25047606', '2.490'])
        self.assertIsNone(log_analyzer.process_line(text_2))

if __name__ == '__main__':
    unittest.main()